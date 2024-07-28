$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#registration_form").on("submit", function(event) {
        event.preventDefault();  // Prevent the default form submission
        registerPlayer($(this));
        return false;
    });

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
});

function registerPlayer(form) {
    var message = form.formToDict();
    message['type'] = "action_new_member";
    message['name'] = message['name'];  // Extract the name from the form
    delete message.body;  // Remove unnecessary fields if any
    updater.socket.send(JSON.stringify(message));
}

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
                case 'game_update_message':
                    updater.updateGame(message);
                    break;
                case 'street_start_message':
                    updater.handleStreetStart(message);
                    break;
                default:
                    window.console.error("received unexpected message: ", message);
            }
        };
    },

    updateGame: function(message) {
        // Log the message data for debugging purposes
        window.console.log("updateGame: ", message);

        // Process the game update message
        const roundState = message.round_state;

        // Update the pot amount
        if (roundState && roundState.pot && roundState.pot.main && roundState.pot.main.amount !== undefined) {
            const potAmount = roundState.pot.main.amount;
            $(".main_pot").text("$" + potAmount);
        }

        // Update other game state if necessary
        // For example, update player states or the community cards
        // $("#table").html(message.table_html || '');
        // $("#event_box").html(message.event_html || '');
    },

    handleStreetStart: function(message) {
        // Log the message data for debugging purposes
        window.console.log("handleStreetStart: ", message);

        // Process the street start message
        const roundState = message.round_state;

        // Example: Update the community cards on the flop
        if (roundState && roundState.community_card) {
            const communityCards = roundState.community_card;
            let communityCardHtml = "";
            communityCards.forEach(card => {
                communityCardHtml += `<img class="card" src="/static/images/card_${card}.png">`;
            });
            $("#community-cards").html(communityCardHtml);
        }

        // Update other parts of the UI if necessary
        // For example, highlight the next player to act
        if (roundState && roundState.next_player !== undefined) {
            $(".player-info").removeClass("highlight");
            $(`#player-${roundState.next_player} .player-info`).addClass("highlight");
        }
    }
};

// Initialize the WebSocket connection
document.addEventListener('DOMContentLoaded', () => {
    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/pokersocket/'
    );

    chatSocket.onopen = function(e) {
        console.log('Chat socket connected successfully');
    };

    chatSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);

            // Log received data
            console.log('Received data:', data);

            // Handle different message types
            if (data.message) {
                document.querySelector('#messages').innerHTML += '<p>' + data.message + '</p>';
            } else if (data.html) {
                document.querySelector('#messages').innerHTML += '<p>Received HTML content</p>';
                console.log('Received HTML content:', data.html);
            } else {
                console.warn('Received data without message property:', data);
            }
        } catch (error) {
            console.error('Error parsing message data:', error, 'Received data:', e.data);
        }
    };

    chatSocket.onerror = function(e) {
        console.error('Chat socket encountered an error:', e);
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly:', e);
    };

    // Function to send a message for testing purposes
    function sendMessage(message) {
        if (chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify(message));
        } else {
            console.error('Chat socket is not open. ReadyState:', chatSocket.readyState);
        }
    }

    // Event listener for the Start Game button
    document.querySelector('#start-game').addEventListener('click', () => {
        sendMessage({
            'type': 'action_start_game'
        });
    });
});








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
    // Usuwa klasę 'active' ze wszystkich przycisków
    var buttons = document.querySelectorAll('.button-action');
    buttons.forEach(function(btn) {
        btn.classList.remove('active');
    });

    // Dodaje klasę 'active' do klikniętego przycisku
    button.classList.add('active');
    
    // Ustala wybraną akcję na podstawie wartości przycisku
    selectedAction = button.value; // Zapisz aktualnie wybraną akcję
}

function declareAction(form) {
    var message = form.formToDict();
    message['type'] = "action_declare_action";
    message['action'] = selectedAction; // Dodaj aktualnie wybraną akcję
    console.log("Wysyłana wiadomość:", message); // Logowanie wiadomości
    updater.socket.send(JSON.stringify(message));
}

// Inicjalizacja, aby dodać obsługę zdarzeń do formularza
$(document).ready(function() {
    $("#declare_action_form").on("submit", function(event) {
        event.preventDefault();  // Zapobiega domyślnej wysyłce formularza
        declareAction($(this));  // Wywołaj funkcję declareAction
        return false;
    });
});



// Upewnij się, że funkcja jest dostępna globalnie
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
            if (message.update_type === 'game_update_message') {
                updater.updateGame(message);
            } else {
                window.console.error("received unexpected message: ", message);
            }
        };
    },

    updateGame: function(message) {
        // Log the message data for debugging purposes
        window.console.log("updateGame: ", message);

        // Process the game update message
        const roundState = message.round_state;

        // Update the pot amount
        if (roundState && roundState.pot && roundState.pot.main && roundState.pot.main.amount !== undefined) {
            const potAmount = roundState.pot.main.amount;
            $(".main_pot").text("$" + potAmount);
        }

        // Update other game state if necessary
        // For example, update player states or the community cards
        // $("#table").html(message.table_html || '');
        // $("#event_box").html(message.event_html || '');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/pokersocket/'
    );

    chatSocket.onopen = function(e) {
        console.log('Chat socket connected successfully');
    };

    chatSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);

            // Log received data
            console.log('Received data:', data);

            // Handle different message types
            if (data.message) {
                document.querySelector('#messages').innerHTML += '<p>' + data.message + '</p>';
            } else if (data.html) {
                document.querySelector('#messages').innerHTML += '<p>Received HTML content</p>';
                console.log('Received HTML content:', data.html);
            } else {
                console.warn('Received data without message property:', data);
            }
        } catch (error) {
            console.error('Error parsing message data:', error, 'Received data:', e.data);
        }
    };

    chatSocket.onerror = function(e) {
        console.error('Chat socket encountered an error:', e);
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly:', e);
    };

    // Function to send a message for testing purposes
    function sendMessage(message) {
        if (chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify(message));
        } else {
            console.error('Chat socket is not open. ReadyState:', chatSocket.readyState);
        }
    }

    // Event listener for the Start Game button
    document.querySelector('#start-game').addEventListener('click', () => {
        sendMessage({
            'type': 'action_start_game'
        });
    });
});
