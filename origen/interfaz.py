import tkinter as tk
from tkinter import messagebox, ttk
from logica import registrar_cliente, listar_clientes, eliminar_cliente

def actualizar_tabla():
    # Limpia la tabla y la vuelve a llenar con los datos de la DB
    for item in tabla.get_children():
        tabla.delete(item)
    for cliente in listar_clientes():
        tabla.insert("", "end", values=cliente)

def guardar():
    nombre = entry_nombre.get()
    telefono = entry_tel.get()
    if nombre and telefono:
        registrar_cliente(nombre, telefono)
        messagebox.showinfo("Éxito", "Cliente guardado correctamente")
        entry_nombre.delete(0, tk.END)
        entry_tel.delete(0, tk.END)
        actualizar_tabla()
    else:
        messagebox.showwarning("Error", "Por favor llena todos los campos")

def borrar():
    selected_item = tabla.selection()
    if selected_item:
        id_cliente = tabla.item(selected_item)['values'][0]
        eliminar_cliente(id_cliente)
        actualizar_tabla()
        messagebox.showinfo("Eliminado", "Cliente borrado")
    else:
        messagebox.showwarning("Atención", "Selecciona un cliente de la tabla")

# Configuración de la Ventana Principal
ventana = tk.Tk()
ventana.title("Sistema Peluquería - Viviana Plata")
ventana.geometry("600x400")

# Formulario
tk.Label(ventana, text="Nombre:").grid(row=0, column=0, padx=10, pady=10)
entry_nombre = tk.Entry(ventana)
entry_nombre.grid(row=0, column=1)

tk.Label(ventana, text="Teléfono:").grid(row=1, column=0, padx=10, pady=10)
entry_tel = tk.Entry(ventana)
entry_tel.grid(row=1, column=1)

btn_guardar = tk.Button(ventana, text="Guardar Cliente", command=guardar, bg="green", fg="white")
btn_guardar.grid(row=2, column=0, columnspan=2, pady=10)

# Tabla para mostrar datos
columnas = ("ID", "Nombre", "Teléfono")
tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=100)
tabla.grid(row=3, column=0, columnspan=2, padx=10)

btn_eliminar = tk.Button(ventana, text="Eliminar Seleccionado", command=borrar, bg="red", fg="white")
btn_eliminar.grid(row=4, column=0, columnspan=2, pady=10)

actualizar_tabla()
ventana.mainloop()
