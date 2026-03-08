from logica import registrar_cliente, listar_clientes, buscar_cliente, editar_cliente, eliminar_cliente
from database import crear_tablas

def menu():
    crear_tablas()
    while True:
        print("\n--- GESTIÓN PELUQUERÍA ---")
        print("1. Registrar | 2. Listar | 3. Buscar")
        print("4. Editar    | 5. Eliminar | 6. Salir")
        op = input("Seleccione: ")
        
        if op == "1":
            n = input("Nombre: "); t = input("Tel: ")
            registrar_cliente(n, t)
        elif op == "2":
            for c in listar_clientes(): print(f"ID: {c[0]} - {c[1]} ({c[2]})")
        elif op == "3":
            n = input("Nombre a buscar: ")
            for c in buscar_cliente(n): print(c)
        elif op == "4":
            id_c = input("ID a editar: ")
            n = input("Nuevo nombre: "); t = input("Nuevo Tel: ")
            editar_cliente(id_c, n, t)
        elif op == "5":
            id_c = input("ID a eliminar: ")
            eliminar_cliente(id_c)
            print("Cliente borrado.")
        elif op == "6": break

if __name__ == "__main__":
    menu()
