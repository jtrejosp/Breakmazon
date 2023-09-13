from flask import Flask, request, jsonify
import datetime
app = Flask(__name__)
# Diccionario para mantener un registro de los usuarios y sus breaks
breaks = {}
# Variable para controlar el usuario con /sissues
sissues_user = None
# Lista de espera para /sissues
sissues_waiting_list = []
@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()
    # Verificar la autenticidad de la solicitud desde Slack (puedes implementar esto)
    # ...
    # Obtener el comando slash y el usuario que lo envió
    command = data.get('command')
    user_id = data.get('user_id')
    if command == '/eos':
        minutes = 8
    elif command == '/pt':
        minutes = 6
    elif command == '/bf':
        minutes = 15
    elif command == '/sissues':
        if sissues_user == user_id:
            # Usuario con /system issues libera el control
            sissues_user = None
            message = f"{user_name} ha liberado el control de system issues."
            while sissues_waiting_list:
                waiting_user = sissues_waiting_list.pop(0)
                start_time = datetime.datetime.now()
                end_time = start_time + datetime.timedelta(minutes=minutes)
                breaks[waiting_user] = {'start_time': start_time, 'end_time': end_time}
                message += f"\n{waiting_user} empieza a las {start_time} y termina a las {end_time}."
        else:
            # Usuario con /sissues obtiene el control
            sissues_user = user_id
            message = f"{sissues_user} tiene el control de system issues. Se agregara a una lista de espera"
            
            # Asigna entrada y salida a los usuarios en la lista de espera
            sissues_waiting_list.append(user_name)
    elif command == '/ntp':
        minutes = 10
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
    # Agregar usuarios a la lista de espera de /sissues
    if command != '/sissues' and user_id != sissues_user:
        sissues_waiting_list.append(user_id)
    # Responder a Slack con un mensaje
    response = {
        "response_type": "in_channel",
        "text": message
    }
    return jsonify(response)
if __name__ == '__main__':
    app.run(debug=True)
