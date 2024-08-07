$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};


    $("#start_game_form").on("submit", function(event) {
        event.preventDefault();  // Prevent the default form submission
        startGame();
        return false;
    });

    $("#declare_action_form").on("submit", function(event) {
        event.preventDefault();  // Prevent the default form submission
        declareAction($(this));
        return false;
    });

    updater.start();

    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/pokersocket/'
    );

    chatSocket.onopen = function(e) {
        console.log('Chat socket connected successfully');
    };

    chatSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);
            if (data.message) {
                document.querySelector('#messages').innerHTML += '<p>' + data.message + '</p>';
            } else if (data.html) {
                document.querySelector('#messages').innerHTML += '<p>Received HTML content</p>';
                console.log('Received HTML content:', data.html);
            } else if (data.update_type) {
                // Custom handling based on update_type
                if (data.update_type === 'game_update_message') {
                    updater.updateGame(data);
                }
            }
        } catch (err) {
            console.error('Error handling chatSocket.onmessage:', err);
        }
    };
    
    

    chatSocket.onerror = function(e) {
        console.error('Chat socket encountered an error:', e);
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly:', e);
    };

    $('#start-game').on('click', function() {
        if (chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({'type': 'action_start_game'}));
        } else {
            console.error('Chat socket is not open. ReadyState:', chatSocket.readyState);
        }
    });

});


function startGame() {
    var message = {};
    message['type'] = "action_start_game";
    updater.socket.send(JSON.stringify(message));
}

function resetGame() {
    var message = {};
    message['type'] = "action_reset_game";
    updater.socket.send(JSON.stringify(message));
}

function activateButton(button) {
    // Remove 'active' class from all buttons
    var buttons = document.querySelectorAll('.button-action');
    buttons.forEach(function(btn) {
        btn.classList.remove('active');
    });

    // Add 'active' class to the clicked button
    button.classList.add('active');
    
    // Set the selected action based on the button value
    selectedAction = button.value; // Save the currently selected action
}

function declareAction(form) {
    var message = form.formToDict();
    message['type'] = "action_declare_action";
    message['action'] = selectedAction; // Add the currently selected action
    console.log("Sending message:", message); // Log the message
    updater.socket.send(JSON.stringify(message));
}

// Ensure the function is globally accessible
window.activateButton = activateButton;

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {};
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/ws/pokersocket/";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            window.console.log("received new message: " + event.data);
            var message = JSON.parse(event.data);
            switch (message.update_type) {
                case 'round_start_message':
                    updater.roundStartMessage(message);
                    break;
                case 'game_update_message':
                    updater.updateGame(message);
                    break;
                case 'street_start_message':
                    updater.handleStreetStart(message);
                    break;
                case 'ask_message':
                    updater.askMessage(message);
                    break;
                case 'round_result_message':
                    updater.roundResultMessage(message);
                    break;
                default:
                    window.console.error("received unexpected message: ", message);
            }
        };
    },

    roundStartMessage: function(message) {
        // Log the message data for debugging purposes
        window.console.log("roundStartMessage: ", message);
    
        const results = message.results;
        const winnerInfo = message.winner_info; // Zakładając, że message zawiera informacje o zwycięzcy
        const winningHand = message.winning_hand; // Zakładając, że message zawiera informacje o zwycięskiej ręce
    
        // Wyświetl informację o wynikach rundy
        const resultContainer = $("#round_results");
        resultContainer.empty(); // Wyczyść poprzednie wyniki
    
        if (results && results.length > 0) {
            results.forEach(result => {
                resultContainer.append(`<p>${result.player_name}: ${result.amount_won}</p>`);
            });
        }
    
        if (winnerInfo) {
            resultContainer.append(`<p>Zwycięzca: ${winnerInfo.name}</p>`);
            if (winningHand) {
                resultContainer.append(`<p>Zwycięska ręka: ${winningHand}</p>`);
            }
        }
    
        // Możesz dodać tutaj inne szczegóły dotyczące wyników rundy, np. pokazane karty graczy itp.
    }, 

    updateGame: function(message) {
        // Log the message data for debugging purposes
        window.console.log("updateGame: ", message);

        const roundState = message.round_state;

        // Update the pot amount
        if (roundState && roundState.pot && roundState.pot.main && roundState.pot.main.amount !== undefined) {
            const potAmount = roundState.pot.main.amount;
            $(".main_pot").text("$" + potAmount);
        }

        // Update the community cards
        const communityCardContainer = $("#community_card");
        communityCardContainer.empty(); // Clear existing cards
        if (roundState.community_card && roundState.community_card.length > 0) {
            roundState.community_card.forEach(card => {
                communityCardContainer.append(`<img class="card" src="/static/images/card_${card}.png" alt="card">`);
            });
        }

        // Update the players
        roundState.seats.forEach(player => {
            const playerDiv = $(`#player-${player.name}`); // Use player.name as identifier
       
            if (playerDiv.length) {
                playerDiv.find(`#player-uuid-${player.name}`).text(`${player.uuid}`);
                playerDiv.find(`#player-stack-${player.name}`).text(`$${player.stack}`);

                if (player.state === "folded") {
                    playerDiv.addClass("folded");
                    console.log(`${player.name} is folded`);
                } else {
                    playerDiv.removeClass("folded");
                }
        
            } else {
                console.warn(`No element found for player ${player.name} with UUID ${player.uuid}`);
            }
        });

        // Update the dealer, small blind, and big blind positions
        $(".label-dealer, .label-blind").remove(); // Clear existing labels
        if (roundState.dealer_btn !== undefined) {
            $(`#player-${roundState.dealer_btn}`).append(`<span class="label-dealer dealer-position-${roundState.dealer_btn}">D</span>`);
        }
        if (roundState.small_blind_pos !== undefined) {
            $(`#player-${roundState.small_blind_pos}`).append(`<span class="label-blind dealer-position-${roundState.small_blind_pos}">SB</span>`);
        }
        if (roundState.big_blind_pos !== undefined) {
            $(`#player-${roundState.big_blind_pos}`).append(`<span class="label-blind dealer-position-${roundState.big_blind_pos}">BB</span>`);
        }

        // Highlight the next player to act
        $(".player-info").removeClass("highlight");
        if (roundState.next_player !== undefined) {
            $(`#player-${roundState.next_player} .player-info`).addClass("highlight");
        }
    },

    handleStreetStart: function(message) {
        // Log the message data for debugging purposes
        window.console.log("handleStreetStart: ", message);

        // Process the street start message
        const roundState = message.round_state;

        // Update the community cards
        if (roundState && roundState.community_card) {
            const communityCards = roundState.community_card;
            let communityCardHtml = "";
            communityCards.forEach(card => {
                communityCardHtml += `<img class="card" src="/static/images/card_${card}.png">`;
            });
            $("#community-cards").html(communityCardHtml);
        }

        // Highlight the next player to act
        if (roundState && roundState.next_player !== undefined) {
            $(".player-info").removeClass("highlight");
            $(`#player-${roundState.next_player} .player-info`).addClass("highlight");
        }
    },

    askMessage: function(message) {
        // Log the message data for debugging purposes
        window.console.log("askMessage: ", message);
    
        // Extract relevant data from the message
        const validActions = message.valid_actions; // Now we use `valid_actions` instead of `action_options`
        const playerName = "Current Player"; // Placeholder since `player_name` is not available in message
    
        // Display the prompt to the player (Hero)
        const promptContainer = $("#action_prompt");
        promptContainer.empty(); // Clear existing prompt
        promptContainer.append(`<h3>${playerName}, it's your turn!</h3>`);
    
        // Add options to the prompt
        validActions.forEach(option => {
            const actionText = option.action; // Get the action name
            const amount = option.amount; // Get the action amount (can be 0 for fold)
            let displayText = actionText;
    
            // Include amount in display text if relevant
            if (amount !== 0 && amount.amount !== undefined) {
                displayText += ` (${amount.amount})`;
            } else if (amount !== 0) {
                displayText += ` (${amount})`;
            }
    
            // Create a button for each valid action
            const button = $(`<button class="action-button">${displayText}</button>`);
            button.on("click", function() {
                updater.sendAction(actionText); // Send the action selected by the player
            });
            promptContainer.append(button);
        });
    
        // Show the prompt container
        promptContainer.show();
    },

    sendAction: function(action) {
        // Send the selected action to the server
        if (updater.socket && updater.socket.readyState === WebSocket.OPEN) {
            const actionMessage = {
                type: "player_action",
                action: action
            };
            updater.socket.send(JSON.stringify(actionMessage));
        } else {
            console.error("WebSocket is not open.");
        }
    },

    roundResultMessage: function(message) {
        // Log the message data for debugging purposes
        window.console.log("roundResultMessage: ", message);
    
        const results = message.results;
        const winnerInfo = message.winner_info; // Zakładając, że message zawiera informacje o zwycięzcy
        const winningHand = message.winning_hand; // Zakładając, że message zawiera informacje o zwycięskiej ręce
    
        // Wyświetl informację o wynikach rundy
        const resultContainer = $("#round_results");
        resultContainer.empty(); // Wyczyść poprzednie wyniki
    
        if (results && results.length > 0) {
            results.forEach(result => {
                resultContainer.append(`<p>${result.player_name}: ${result.amount_won}</p>`);
            });
        }
    
        if (winnerInfo) {
            resultContainer.append(`<p>Zwycięzca: ${winnerInfo.name}</p>`);
            if (winningHand) {
                resultContainer.append(`<p>Zwycięska ręka: ${winningHand}</p>`);
            }
        }
    
        // Możesz dodać tutaj inne szczegóły dotyczące wyników rundy, np. pokazane karty graczy itp.
    }
};


// Initialize the WebSocket connection
// document.addEventListener('DOMContentLoaded', () => {
//     const chatSocket = new WebSocket(
//         'ws://' + window.location.host + '/ws/pokersocket/'
//     );

//     chatSocket.onopen = function(e) {
//         console.log('Chat socket connected successfully');
//     };

//     chatSocket.onmessage = function(e) {
//         try {
//             const data = JSON.parse(e.data);
//             if (data.message) {
//                 document.querySelector('#messages').innerHTML += '<p>' + data.message + '</p>';
//             } else if (data.html) {
//                 document.querySelector('#messages').innerHTML += '<p>Received HTML content</p>';
//                 console.log('Received HTML content:', data.html);
//             } else if (data.update_type) {
//                 // Custom handling based on update_type
//                 if (data.update_type === 'game_update_message') {
//                     updater.updateGame(data);
//             }
//     };
    
    

//     chatSocket.onerror = function(e) {
//         console.error('Chat socket encountered an error:', e);
//     };

//     chatSocket.onclose = function(e) {
//         console.error('Chat socket closed unexpectedly:', e);
//     };

//     // Function to send a message for testing purposes
//     function sendMessage(message) {
//         if (chatSocket.readyState === WebSocket.OPEN) {
//             chatSocket.send(JSON.stringify(message));
//         } else {
//             console.error('Chat socket is not open. ReadyState:', chatSocket.readyState);
//         }
//     }

//     // Event listener for the Start Game button
//     document.querySelector('#start-game').addEventListener('click', () => {
//         sendMessage({
//             'type': 'action_start_game'
//         });
//     });
// });
