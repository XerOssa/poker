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

function declareAction(form) {
    var message = form.formToDict();
    message['type'] = "action_declare_action";
    updater.socket.send(JSON.stringify(message));
}

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
            if (message['message_type'] === 'config_update') {
                updater.updateConfig(message);
            } else if (message['message_type'] === 'start_game') {
                updater.startGame(message);
            } else if (message['message_type'] === 'update_game') {
                updater.updateGame(message);
            } else if (message['message_type'] === 'alert_restart_server') {
                updater.alertRestartServer(message);
            } else {
                window.console.error("received unexpected message: " + message);
            }
        };
    },

    updateConfig: function(message) {
        var node = $(message.html);
        $("#config_box").html(node);
        if (message.registered) {
            $("#registration_form input[type=submit]").prop("disabled", true);
        }
    },

    startGame: function(message) {
        var node = $(message.html);
        $("#container").html(node);
        $("#declare_action_form").hide();
        $("#declare_action_form").on("submit", function(event) {
            event.preventDefault();  // Prevent the default form submission
            declareAction($(this));
            return false;
        });
    },

    updateGame: function(message) {
        $("#declare_action_form").hide();
        var content = message['content'];
        window.console.log("updateGame: " + JSON.stringify(content));
        var messageType = content['update_type'];
        if (messageType === 'round_start_message') {
            updater.roundStart(content.event_html);
        } else if (messageType === 'street_start_message') {
            updater.newStreet(content.table_html, content.event_html);
        } else if (messageType === 'game_update_message') {
            updater.newAction(content.table_html, content.event_html);
        } else if (messageType === 'round_result_message') {
            updater.roundResult(content.table_html, content.event_html);
        } else if (messageType === 'game_result_message') {
            updater.gameResult(content.event_html);
        } else if (messageType === 'ask_message') {
            $("#declare_action_form").show();
            updater.askAction(content.table_html, content.event_html);
        } else {
            window.console.error("unexpected message in updateGame: " + content);
        }

        // Aktualizacja wartości potu
        var potAmount = content.round_state.pot.main.amount;
        if (potAmount !== undefined) {
            $(".pot .main_pot").text("$" + potAmount);
        }
    },

    roundStart: function(eventHtml) {
        $("#event_box").html($(eventHtml));
    },

    newStreet: function(tableHtml, eventHtml) {
        $("#table").html($(tableHtml));
        $("#event_box").html($(eventHtml));
    },

    newAction: function(tableHtml, eventHtml) {
        $("#table").html($(tableHtml));
        $("#event_box").html($(eventHtml));
    },

    roundResult: function(tableHtml, eventHtml) {
        $("#table").html($(tableHtml));
        $("#event_box").html($(eventHtml));
    },

    gameResult: function(eventHtml) {
        $("#event_box").html($(eventHtml));
    },

    askAction: function(tableHtml, eventHtml) {
        $("#table").html($(tableHtml));
        $("#event_box").html($(eventHtml));
    },

    alertRestartServer: function(message) {
        alert(message.message);
    }
};
