from controller import Supervisor, Camera, Motor, DistanceSensor, GPS

TIME_STEP = 32
FORWARD_SPEED = 5.0
TURN_SPEED = 2.5

# Función para detectar una columna roja
def detectar_columna(camera):
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()
    red_pixels = 0

    for x in range(width // 3, 2 * width // 3):
        for y in range(height // 3, 2 * height // 3):
            r = Camera.imageGetRed(image, width, x, y)
            g = Camera.imageGetGreen(image, width, x, y)
            b = Camera.imageGetBlue(image, width, x, y)

            if r > 150 and g < 100 and b < 100:
                red_pixels += 1

    return red_pixels > 50

# Función para obtener fila y columna basada en la posición
def obtener_fila_columna(position, arena_center, arena_size, num_filas, num_columnas):
    x, _, z = position  # Ignoramos y (altura)
    center_x, _, center_z = arena_center
    size_x, _, size_z = arena_size
    
    # Coordenadas relativas al borde del arena
    relative_x = x - (center_x - size_x / 2)
    relative_z = z - (center_z - size_z / 2)
    
    # Tamaño de cada celda
    cell_width = size_x / num_columnas
    cell_height = size_z / num_filas

    # Calcular fila y columna
    columna = int(relative_x // cell_width)
    fila = int(relative_z // cell_height)

    return fila, columna

# Inicializar Supervisor
robot = Supervisor()

# Dispositivos
camera = robot.getDevice('camera')
camera.enable(TIME_STEP)

gps = robot.getDevice('gps')
gps.enable(TIME_STEP)

front_sensor = robot.getDevice('so11')
front_sensor.enable(TIME_STEP)

# Motores
left_front_motor = robot.getDevice('front left wheel')
right_front_motor = robot.getDevice('front right wheel')
left_rear_motor = robot.getDevice('back left wheel')
right_rear_motor = robot.getDevice('back right wheel')

motors = [left_front_motor, right_front_motor, left_rear_motor, right_rear_motor]

for motor in motors:
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)

# Obtener el arena
arena_box = robot.getFromDef('arena_bounding_box')
bounding_box = arena_box.getField('boundingObject').getSFNode()
arena_size_vec = bounding_box.getField('size').getSFVec3f()
arena_size = [arena_size_vec[0], 0, arena_size_vec[2]]


# Bucle principal
while robot.step(TIME_STEP) != -1:
    # Movimiento hacia adelante
    for motor in motors:
        motor.setVelocity(FORWARD_SPEED)

    # Si detecta obstáculo cercano (por distancia)
    if front_sensor.getValue() < 950:  # Ajusta el valor si es necesario
        print("Obstáculo detectado, clasificando...")

        # Detener motores
        for motor in motors:
            motor.setVelocity(0.0)
        robot.step(500)

        # Obtener posición actual
        position = gps.getValues()
        fila, columna = obtener_fila_columna(position, arena_center, arena_size, 5, 5)  # 5x5 es ejemplo
        print(f"Fila: {fila}, Columna: {columna}")

        resultado = fila + columna
        print(f"Resultado fila + columna: {resultado}")

        # Decidir hacia donde girar
        if resultado % 2 == 0:
            print("Resultado par, moviendo a la izquierda...")
            # Girar izquierda
            left_front_motor.setVelocity(-TURN_SPEED)
            right_front_motor.setVelocity(TURN_SPEED)
            left_rear_motor.setVelocity(-TURN_SPEED)
            right_rear_motor.setVelocity(TURN_SPEED)
        else:
            print("Resultado impar, moviendo a la derecha...")
            # Girar derecha
            left_front_motor.setVelocity(TURN_SPEED)
            right_front_motor.setVelocity(-TURN_SPEED)
            left_rear_motor.setVelocity(TURN_SPEED)
            right_rear_motor.setVelocity(-TURN_SPEED)

        robot.step(1000)  # Gira durante un tiempo

        # Volver a avanzar
        for motor in motors:
            motor.setVelocity(FORWARD_SPEED)
