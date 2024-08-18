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

function declareAction(form) {
    const message = form.formToDict();
    message['type'] = "action_declare_action";
    message['action'] = selectedAction; // Wcześniej wybrana akcja
    console.log("Sending message:", message); // Loguj wiadomość
    sendWebSocketMessage("action_declare_action", message);
}

function activateButton(button) {
    $('.button-action').removeClass('active');
    button.classList.add('active');
    selectedAction = button.value; // Zapisz aktualnie wybraną akcję
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
        this.socket.onclose = e => console.error('WebSocket closed unexpectedly:', e);
    },

    handleMessage: function(event) {
        console.log("Raw WebSocket data:", event.data);
        try {
            const message = JSON.parse(event.data);
            console.log("Parsed WebSocket message:", message);

            if (message.update_type) {
                updater.handleUpdate(message);
            } else if (message.message) {
                updater.displayChatMessage(message.message);
            } else if (message.html) {
                updater.displayHtmlMessage(message.html);
            } else {
                console.warn("Unknown message format:", message);
            }
        } catch (err) {
            console.error('Error handling WebSocket message:', err);
        }
    },

    handleUpdate: function(message) {
        switch (message.update_type) {
            case 'round_start_message':
                this.roundStartMessage(message);
                break;
            case 'game_update_message':
                this.updateGame(message);
                break;
            case 'street_start_message':
                this.handleStreetStart(message);
                break;
            case 'ask_message':
                this.askMessage(message);
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
        console.log("roundStartMessage received:", message);

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
        console.log("updateGame:", message);

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
        roundState.seats.forEach(this.updatePlayerState);

        // Aktualizacja pozycji dealera, małej i dużej ciemnej
        this.updateBlinds(roundState);

        // Podświetlenie następnego gracza
        $(".player-info").removeClass("highlight");
        if (roundState.next_player !== undefined) {
            $(`#player-${roundState.next_player} .player-info`).addClass("highlight");
        }
    },

    updatePlayerState: function(player) {
        const playerDiv = $(`#player-${player.name}`);

        if (playerDiv.length) {
            playerDiv.find(`#player-uuid-${player.name}`).text(`${player.uuid}`);
            playerDiv.find(`#player-stack-${player.name}`).text(`$${player.stack}`);

            playerDiv.toggleClass('folded', player.state === "folded");
        } else {
            console.warn(`No element found for player ${player.name}`);
        }
    },

    updateBlinds: function(roundState) {
        $(".label-dealer, .label-blind").remove();

        if (roundState.dealer_btn !== undefined) {
            $(`#player-${roundState.dealer_btn}`).append('<span class="label-dealer">D</span>');
        }
        if (roundState.small_blind_pos !== undefined) {
            $(`#player-${roundState.small_blind_pos}`).append('<span class="label-blind">SB</span>');
        }
        if (roundState.big_blind_pos !== undefined) {
            $(`#player-${roundState.big_blind_pos}`).append('<span class="label-blind">BB</span>');
        }
    },

    handleStreetStart: function(message) {
        console.log("handleStreetStart:", message);

        const communityCardContainer = $("#community-cards");
        communityCardContainer.empty();
        message.round_state.community_card.forEach(card => {
            communityCardContainer.append(`<img class="card" src="/static/images/card_${card}.png">`);
        });

        $(".player-info").removeClass("highlight");
        if (message.round_state.next_player !== undefined) {
            $(`#player-${message.round_state.next_player} .player-info`).addClass("highlight");
        }
    },

    askMessage: function(message) {
        console.log("askMessage received:", message);

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
    },

    sendAction: function(action) {
        sendWebSocketMessage("player_action", { action });
    },

    roundResultMessage: function(message) {
        console.log("roundResultMessage received:", message);

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
