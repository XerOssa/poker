$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    // Zainicjuj WebSocket
    updater.start();

    // Obsługa formularzy i przycisków
    $("#start_game_form").on("submit", handleFormSubmit.bind(null, startGame));
    $("#declare_action_form").on("submit", handleFormSubmit.bind(null, declareAction));
    $('#start-game').on('click', () => sendWebSocketMessage('action_start_game'));
});

function handleFormSubmit(actionFunction, event) {
    event.preventDefault();
    actionFunction($(this));
    return false;
}

function sendWebSocketMessage(type, additionalData = {}) {
    const message = { type, ...additionalData };
    if (updater.socket && updater.socket.readyState === WebSocket.OPEN) {
        updater.socket.send(JSON.stringify(message));
    } else {
        console.error("WebSocket is not open.");
    }
}

function startGame() {
    sendWebSocketMessage("action_start_game");
}

function activateButton(button) {
    $('.button-action').removeClass('active');
    button.classList.add('active');
    selectedAction = button.value; // Zapisz aktualnie wybraną akcję

    // Sprawdź, czy akcja to 'raise' i dostosuj widoczność pola kwoty
    if (selectedAction === 'raise') {
        $("#raise-amount-container").show(); // Pokaż pole dla kwoty
    } else {
        $("#raise-amount-container").hide(); // Ukryj pole dla kwoty
    }
}

function declareAction(form) {
    const message = form.formToDict();
    message['type'] = "action_declare_action";
    message['action'] = selectedAction; // Wcześniej wybrana akcja

    if (selectedAction === 'raise') {
        const rawAmount = $("#raise-amount").val().trim(); // Pobierz wartość z formularza i usuń białe znaki
        const parsedAmount = parseInt(rawAmount, 10); // Przekształć wartość na liczbę całkowitą

        if (isNaN(parsedAmount) || parsedAmount <= 0) { // Sprawdź, czy wartość jest prawidłowa
            alert("Please enter a valid raise amount");
            return;
        }

        message['amount'] = parsedAmount;  // Ustaw prawidłową wartość
    }

    console.log("Hero decision:", message); // Loguj wiadomość
    sendWebSocketMessage("action_declare_action", message);
}



function highlightNextPlayer(nextPlayerId) {
    $(".player-info").removeClass("highlight"); // Usuń podświetlenie od wszystkich
    if (nextPlayerId !== undefined) {
        $(`#player-${nextPlayerId} .player-info`).addClass("highlight"); // Dodaj podświetlenie tylko do następnego gracza
    }
}

// Globalna funkcja
window.activateButton = activateButton;

jQuery.fn.formToDict = function() {
    const fields = this.serializeArray();
    const json = {};
    fields.forEach(field => json[field.name] = field.value);
    if (json.next) delete json.next;
    return json;
};

// Obiekt odpowiedzialny za całą logikę WebSocket oraz aktualizacje gry
const updater = {
    socket: null,

    start: function() {
        const url = "ws://" + location.host + "/ws/pokersocket/";
        this.socket = new WebSocket(url);

        this.socket.onopen = () => console.log('WebSocket connected successfully');
        this.socket.onmessage = this.handleMessage;
        this.socket.onerror = e => console.error('WebSocket error:', e);
        this.socket.onclose = e => {
            console.error('WebSocket closed unexpectedly:', e);
            // Attempt to reconnect after a delay
            setTimeout(() => this.start(), 5000); // Retry after 5 seconds
        };
    },

    handleMessage: function(event) {
        try {
            const message = JSON.parse(event.data);
            if (message.update_type) {
                updater.handleUpdate(message);
            } else {
                console.warn("Unknown message format:", message);
            }
        } catch (err) {
            console.error('Error handling WebSocket message:', err);
        }
    },

    handleUpdate: function(message) {
        switch (message.update_type) {
            case 'street_start_message':
                this.handleStreetStart(message);
                break;
            case 'ask_message':
                // Opóźnienie wywołania askMessage, aby upewnić się, że karty wspólne zostały już wyrenderowane
                setTimeout(() => {
                    this.askMessage(message);
                }, 200); // Ustawienie krótkiego opóźnienia, aby wyrenderować karty
                break;
            case 'round_start_message':
                this.roundStartMessage(message);
                break;
            case 'game_update_message':
                this.updateGame(message);
                break;
            case 'round_result_message':
                this.roundResultMessage(message);
                break;
            default:
                console.error("Unexpected message type:", message.update_type);
        }
    },

    displayChatMessage: function(message) {
        $('#messages').append('<p>' + message + '</p>');
    },

    displayHtmlMessage: function(html) {
        $('#messages').append('<p>Received HTML content</p>');
        console.log('Received HTML content:', html);
    },

    roundStartMessage: function(message) {
        console.log("Start round:", message);

        const playerName = "Jacek";
        const playerCardsContainer = $(`#player-cards-${playerName}`);
        playerCardsContainer.empty(); // Wyczyść poprzednie karty

        if (message.hole_card && message.hole_card.length) {
            message.hole_card.forEach(card => {
                playerCardsContainer.append(`<img class="card" src="/static/images/card_${card}.png">`);
            });
        } else {
            console.warn("No hole cards received.");
        }
    },

    updateGame: function(message) {
        console.log("Game update:", message);
    
        const roundState = message.round_state;
    
        // Aktualizacja puli głównej
        if (roundState.pot && roundState.pot.main) {
            $(".main_pot").text("$" + roundState.pot.main.amount);
        }
    
        // Aktualizacja kart wspólnych
        const communityCardContainer = $("#community_card");
        communityCardContainer.empty();
        roundState.community_card.forEach(card => {
            communityCardContainer.append(`<img class="card" src="/static/images/card_${card}.png" alt="card">`);
        });
    
        // Aktualizacja graczy
        roundState.seats.forEach(this.updatePlayerState.bind(this));
    
        // Aktualizacja pozycji dealera, małej i dużej ciemnej
        this.updateBlinds(roundState);
    
        highlightNextPlayer(roundState.next_player); // Podświetlenie następnego gracza
    },


    updatePlayerState: function(player) {
        const playerDiv = $(`#player-${player.name}`);
        if (playerDiv.length) {
            playerDiv.find(`#player-uuid-${player.name}`).text(`${player.uuid}`);
            playerDiv.find(`#player-stack-${player.name}`).text(`$${player.stack}`);
            
            // Add or remove the 'inactive' class based on the player's state
            if (player.state === "folded") {
                playerDiv.find('.material-icons').addClass('inactive');
            } else {
                playerDiv.find('.material-icons').removeClass('inactive');
            }
        }
    },
    

    updateBlinds: function(roundState) {
        $(".label-dealer, .label-blind").remove();

        if (roundState.dealer_btn !== undefined) {
            $(`#player-${roundState.dealer_btn}`).append(`<span class="label-dealer dealer-position-${roundState.dealer_btn}">D</span>`);
        }
        if (roundState.small_blind_pos !== undefined) {
            $(`#player-${roundState.small_blind_pos}`).append(`<span class="label-blind dealer-position-${roundState.small_blind_pos}">SB</span>`);
        }
        if (roundState.big_blind_pos !== undefined) {
            $(`#player-${roundState.big_blind_pos}`).append(`<span class="label-blind dealer-position-${roundState.big_blind_pos}">BB</span>`);
        }
    },

    handleStreetStart: function(message) {
        console.log("Start street:", message);
        console.log("Karty wspólne przed renderowaniem:", message.round_state.community_card);
    
        const communityCardContainer = $("#community-cards");
        communityCardContainer.empty();
    
        message.round_state.community_card.forEach(card => {
            communityCardContainer.append(`<img class="card" src="/static/images/card_${card}.png">`);
        });
    
        highlightNextPlayer(message.round_state.next_player);
        console.log("Karty wspólne po renderowaniu.");
    },

    askMessage: function(message) {
        console.log("Hero have decision", message);
    
        // Daj niewielkie opóźnienie przed wyświetleniem opcji decyzji gracza
        setTimeout(() => {
            const promptContainer = $("#action_prompt");
            promptContainer.empty().append(`<h3>It's your turn!</h3>`);
    
            message.valid_actions.forEach(action => {
                let displayText = action.action;
                if (action.amount !== 0) {
                    displayText += ` (${action.amount.amount || action.amount})`;
                }
                const button = $(`<button class="action-button">${displayText}</button>`);
                button.on("click", () => this.sendAction(action.action));
                promptContainer.append(button);
            });
    
            promptContainer.show();
            highlightNextPlayer(message.round_state.next_player);
        }, 500); // Opóźnienie 100ms
    },

    sendAction: function(action) {
        sendWebSocketMessage("player_action", { action });
    },

    roundResultMessage: function(message) {
        console.log("roundResult:", message);

        const resultContainer = $("#round_results");
        resultContainer.empty();

        if (message.results) {
            message.results.forEach(result => {
                resultContainer.append(`<p>${result.player_name}: ${result.amount_won}</p>`);
            });
        }

        if (message.winner_info) {
            resultContainer.append(`<p>Winner: ${message.winner_info.name}</p>`);
            if (message.winning_hand) {
                resultContainer.append(`<p>Winning hand: ${message.winning_hand}</p>`);
            }
        }
    }
};
