from database import conectar

def registrar_cliente(nombre, telefono):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nombre, telefono) VALUES (?, ?)", (nombre, telefono))
    conn.commit()
    conn.close()

def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    res = cursor.fetchall()
    conn.close()
    return res

def buscar_cliente(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE nombre LIKE ?", ('%' + nombre + '%',))
    res = cursor.fetchall()
    conn.close()
    return res

def editar_cliente(id_cliente, nuevo_nombre, nuevo_tel):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE clientes SET nombre = ?, telefono = ? WHERE id = ?", (nuevo_nombre, nuevo_tel, id_cliente))
    conn.commit()
    conn.close()

def eliminar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    conn.close()
