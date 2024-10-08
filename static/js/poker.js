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

function startGame() {
    sendWebSocketMessage("action_start_game");
}

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



function activateButton(button) {
    $('.button-action').removeClass('active');
    button.classList.add('active');
    selectedAction = button.value; // Zapisz aktualnie wybraną akcję
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
            setTimeout(() => this.start(), 2000); // Retry after 5 seconds
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
            case 'round_start_message':
                this.roundStartMessage(message);
                break;
            case 'street_start_message':
                this.streetStartMessage(message);
                break;
            case 'ask_message':
                this.askMessage(message);
                break;
            case 'game_update_message':
                this.updateGame(message);
                break;
            case 'round_result_message':
                this.roundResultMessage(message);
                break;
            case 'game_result_message':
                this.gameResultMessage(message);
                break;
            default:
                console.error("Unexpected message type:", message.update_type);
        }
    },


    roundStartMessage: function(message) {
        console.log("Start round:", message);
    
        // Zakładamy, że nazwa gracza to 'hero'
        const heroName = message.hero_name;  // Nazwa gracza z wiadomości, może to być również np. message.player_uuid
        const playerCardsContainer = $(`#player-cards-${heroName}`);
        
        playerCardsContainer.empty();  // Czyścimy karty przed nową rundą
        
        // Sprawdzamy, czy mamy dostępne karty hole_card
        if (message.hole_card && message.hole_card.length) {
            console.log("Hero ma:", message.hole_card);
            playerCardsContainer.show();
            
            // Renderujemy karty
            message.hole_card.forEach(card => {
                playerCardsContainer.append(`<img class="card" src="/static/images/card_${card}.png" alt="${card}">`);
            });
        } else {
            console.warn(`${playerName} nie otrzymał kart hole_card.`);
        }
    },
    
    

    streetStartMessage: function(message) {
        console.log("Start street:", message);
        this.renderCommunityCards(message.round_state.community_card);
        this.highlightNextPlayer(message.round_state.next_player);
        const roundState = message.round_state;
        this.updateBlinds(roundState);  
    },


    askMessage: function(message) {
        console.log("Hero have decision", message);
        this.updateCommunityCards(message.round_state.community_card);
        this.displayPlayerActions(message.valid_actions);
        this.highlightNextPlayer(message.round_state.next_player);      // FIXME: usuniecie timeout
    },


    updateGame: function(message) {
        console.log("Game update:", message);
        const roundState = message.round_state;
        // this.updateBlinds(roundState);                                                  // FIXME: zmiana kolejniosci
        if (roundState.pot && roundState.pot.main) {
            $(".main_pot").text("$" + roundState.pot.main.amount);
        }
        this.updateCommunityCards(roundState.community_card);
        // Aktualizacja graczy
        
        roundState.seats.forEach(this.updatePlayerState.bind(this));
        
        highlightNextPlayer(roundState.next_player); // Podświetlenie następnego gracza
    },


    roundResultMessage: function(message) {
        console.log("round Result:", message);
        const resultContainer = $("#round_results");
        resultContainer.empty();
    },

    gameResultMessage: function(message) {
        console.log("game Result:", message);

        const resultContainer = $("#game_results");
        resultContainer.empty();
    },


    updateCommunityCards: function(communityCards) {
        const communityCardContainer = $("#community_card");
        communityCardContainer.empty();
        communityCards.forEach(card => {
            communityCardContainer.append(`<img class="card" src="/static/images/card_${card}.png" alt="card">`);
        });
    },


    updatePlayerState: function(player) {
        // console.log("wiadomosc player:", player);
        const playerDiv = $(`#player-${player.name}`);
        if (playerDiv.length) {
            playerDiv.find(`#player-uuid-${player.name}`).text(`${player.uuid}`);
            playerDiv.find(`#player-stack-${player.name}`).text(`$${player.stack}`);

            if (player.state === "folded") {
                playerDiv.find('.material-icons').addClass('inactive');
                playerDiv.find(`#player-cards-human`).hide(); // Ukryj karty, jeśli gracz spasował
            } else {
                playerDiv.find('.material-icons').removeClass('inactive');
                playerDiv.find(`#player-cards-human`).show(); // Pokaż karty, jeśli gracz jest aktywny
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


    
    renderCommunityCards: function(communityCards) {
        const communityCardContainer = $("#community-cards");
        communityCardContainer.empty();
    
        communityCards.forEach(card => {
            communityCardContainer.append(`<img class="card" src="/static/images/card_${card}.png">`);
        });
    
    },
    
    highlightNextPlayer: function(nextPlayerId) {
        $(".player-info").removeClass("highlight");
        if (nextPlayerId !== undefined) {
            $(`#player-${nextPlayerId} .player-info`).addClass("highlight");
        }
    },


    
    displayPlayerActions: function(validActions) {
        const promptContainer = $("#action_prompt");
        promptContainer.empty().append(`<h3>It's your turn!</h3>`);
    
        validActions.forEach(action => {
            const button = this.createActionButton(action);
            promptContainer.append(button);
        });
    
        promptContainer.show();
    },
    
    createActionButton: function(action) {
        let displayText = action.action;
        if (action.amount !== 0) {
            displayText += ` (${action.amount.amount || action.amount})`;
        }
    
        const button = $(`<button class="action-button">${displayText}</button>`);
        button.on("click", () => this.sendAction(action.action));
    
        return button;
    },
    
    sendAction: function(action) {
        sendWebSocketMessage("player_action", { action });
    },
    
    // displayChatMessage: function(message) {
    //     $('#messages').append('<p>' + message + '</p>');
    // },

    // displayHtmlMessage: function(html) {
    //     $('#messages').append('<p>Received HTML content</p>');
    //     console.log('Received HTML content:', html);
    // },

};