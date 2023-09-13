from flask import Flask, request, jsonify
import datetime
app = Flask(__name__)
# Diccionario para mantener un registro de los usuarios y sus breaks
breaks = {}
# Variable para controlar el usuario con /sissues
sissues_user = None
# Diccionario para mapear IDs de usuario a nombres de usuario
user_names = {
    "USER_ID_1": "Usuario1",
    "USER_ID_2": "Usuario2",
    # Agrega más mapeos de ID de usuario a nombre de usuario aquí
}
@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()
    # Verificar la autenticidad de la solicitud desde Slack (puedes implementar esto)
    # ...
    # Obtener el comando slash y el usuario que lo envió
    command = data.get('command')
    user_id = data.get('user_id')
    # Obtener el nombre de usuario a partir del ID de usuario
    user_name = user_names.get(user_id, "Usuario Desconocido")
    if command == '/eos':
        minutes = 8
    elif command == '/pt':
        minutes = 6
    elif command == '/bf':
        minutes = 15
    elif command == '/ntp':
        minutes = 10
    elif command == '/sissues':
        if sissues_user == user_id:
            # Usuario con /sissues libera el control
            sissues_user = None
            message = f"{user_name} ha liberado el control de /sissues."
        else:
            # Usuario con /sissues obtiene el control
            sissues_user = user_id
            message = f"{user_name} tiene el control de /sissues. Nadie más puede pedir breaks."
    if user_id in breaks:
        # Usuario ya está en break
        next_break = breaks[user_id]['end_time']
        message = f"{user_name}, ya estás en break hasta las {next_break}."
    elif sissues_user != user_id:
        # Otro usuario tiene el control de /sissues
        message = f"Espera a que {user_name} libere el control de /sissues."
    else:
        # Calcular el tiempo de inicio y finalización del break
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=minutes)
        breaks[user_id] = {'start_time': start_time, 'end_time': end_time}
        message = f"{user_name}, tu break empieza a las {start_time} y termina a las {end_time}."
    # Responder a Slack con un mensaje
    response = {
        "response_type": "in_channel",
        "text": message
    }
    return jsonify(response)
if __name__ == '__main__':
    app.run(debug=True)
