import sqlite3
from rich.console import Console
from rich.table import Table
from tabulate import tabulate

console = Console()

def inicializar_db():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Proveedor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        direccion TEXT,
        telefono TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bodega (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ubicacion TEXT,
        capacidad_maxima INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL,
        stock INTEGER,
        categoria_id INTEGER,
        proveedor_id INTEGER,
        bodega_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES Categoria(id),
        FOREIGN KEY (proveedor_id) REFERENCES Proveedor(id),
        FOREIGN KEY (bodega_id) REFERENCES Bodega(id)
    )
    ''')

    conn.commit()
    conn.close()


def eliminar_todos_los_datos():
    confirmacion = input("¿Está seguro de que desea eliminar todos los datos? Esta acción no se puede deshacer (s/n): ").lower()
    if confirmacion == 's':
        conn = sqlite3.connect('GestionInventario.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Producto")
        cursor.execute("DELETE FROM Categoria")
        cursor.execute("DELETE FROM Proveedor")
        cursor.execute("DELETE FROM Bodega")
        
        conn.commit()
        conn.close()
        console.print("[bold red]Todos los datos han sido eliminados.[/bold red]")
    else:
        console.print("[bold green]Operación cancelada. No se han eliminado datos.[/bold green]")

def agregar_categoria(nombre, descripcion):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Categoria (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    conn.commit()
    conn.close()

def agregar_proveedor(nombre, direccion, telefono, productos):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Proveedor (nombre, direccion, telefono) VALUES (?, ?, ?)", (nombre, direccion, telefono))
    proveedor_id = cursor.lastrowid
    for producto in productos:
        cursor.execute("UPDATE Producto SET proveedor_id = ? WHERE nombre = ?", (proveedor_id, producto))
    conn.commit()
    conn.close()

def agregar_bodega(nombre, ubicacion, capacidad_maxima, productos):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Bodega (nombre, ubicacion, capacidad_maxima) VALUES (?, ?, ?)", (nombre, ubicacion, capacidad_maxima))
    bodega_id = cursor.lastrowid
    for producto in productos:
        cursor.execute("UPDATE Producto SET bodega_id = ? WHERE nombre = ?", (bodega_id, producto))
    conn.commit()
    conn.close()

def agregar_producto(nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Producto (nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id))
    conn.commit()
    conn.close()

def eliminar_producto(nombre):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Producto WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()
    console.print("[bold green]Producto eliminado exitosamente.[/bold green]")

def consultar_producto(nombre):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, c.nombre AS categoria, pr.nombre AS proveedor, b.nombre AS bodega
    FROM Producto p
    LEFT JOIN Categoria c ON p.categoria_id = c.id
    LEFT JOIN Proveedor pr ON p.proveedor_id = pr.id
    LEFT JOIN Bodega b ON p.bodega_id = b.id
    WHERE p.nombre = ?
    ''', (nombre,))
    producto = cursor.fetchone()
    conn.close()
    if producto:
        table = tabulate([producto], headers=['ID', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría', 'Proveedor', 'Bodega'], tablefmt='fancy_grid')
        console.print(table)
    else:
        console.print("[bold red]Producto no encontrado.[/bold red]")

def consultar_categoria(nombre):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, descripcion FROM Categoria WHERE nombre = ?', (nombre,))
    categoria = cursor.fetchone()
    if categoria:
        cursor.execute('''
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock
        FROM Producto p
        WHERE p.categoria_id = ?
        ''', (categoria[0],))
        productos = cursor.fetchall()
        conn.close()
        table = tabulate([categoria], headers=['ID', 'Nombre', 'Descripción'], tablefmt='fancy_grid')
        console.print(table)
        if productos:
            console.print("\n[bold]Productos en esta categoría:[/bold]")
            table = tabulate(productos, headers=['ID', 'Nombre', 'Descripción', 'Precio', 'Stock'], tablefmt='fancy_grid')
            console.print(table)
        else:
            console.print("[bold red]No hay productos en esta categoría.[/bold red]")
    else:
        console.print("[bold red]Categoría no encontrada.[/bold red]")

def consultar_proveedor(nombre):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, direccion, telefono FROM Proveedor WHERE nombre = ?', (nombre,))
    proveedor = cursor.fetchone()
    if proveedor:
        cursor.execute('''
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock
        FROM Producto p
        WHERE p.proveedor_id = ?
        ''', (proveedor[0],))
        productos = cursor.fetchall()
        conn.close()
        table = tabulate([proveedor], headers=['ID', 'Nombre', 'Dirección', 'Teléfono'], tablefmt='fancy_grid')
        console.print(table)
        if productos:
            console.print("\n[bold]Productos suministrados por este proveedor:[/bold]")
            table = tabulate(productos, headers=['ID', 'Nombre', 'Descripción', 'Precio', 'Stock'], tablefmt='fancy_grid')
            console.print(table)
        else:
            console.print("[bold red]No hay productos suministrados por este proveedor.[/bold red]")
    else:
        console.print("[bold red]Proveedor no encontrado.[/bold red]")

def consultar_bodega(nombre):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, ubicacion, capacidad_maxima FROM Bodega WHERE nombre = ?', (nombre,))
    bodega = cursor.fetchone()
    if bodega:
        cursor.execute('''
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock
        FROM Producto p
        WHERE p.bodega_id = ?
        ''', (bodega[0],))
        productos = cursor.fetchall()
        conn.close()
        table = tabulate([bodega], headers=['ID', 'Nombre', 'Ubicación', 'Capacidad Máxima'], tablefmt='fancy_grid')
        console.print(table)
        if productos:
            console.print("\n[bold]Productos en esta bodega:[/bold]")
            table = tabulate(productos, headers=['ID', 'Nombre', 'Descripción', 'Precio', 'Stock'], tablefmt='fancy_grid')
            console.print(table)
        else:
            console.print("[bold red]No hay productos en esta bodega.[/bold red]")
    else:
        console.print("[bold red]Bodega no encontrada.[/bold red]")

def agregar_stock(nombre_producto, cantidad):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET stock = stock + ? WHERE nombre = ?", (cantidad, nombre_producto))
    conn.commit()
    conn.close()
    console.print("[bold green]Stock agregado exitosamente.[/bold green]")

def retirar_stock(nombre_producto, cantidad):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET stock = stock - ? WHERE nombre = ?", (cantidad, nombre_producto))
    conn.commit()
    conn.close()
    console.print("[bold green]Stock retirado exitosamente.[/bold green]")

def calcular_valor_total_stock():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(precio * stock) FROM Producto')
    valor_total = cursor.fetchone()[0]
    conn.close()
    console.print(f"[bold]Valor total del stock: {valor_total}[/bold]")

def agregar_producto_a_categoria(producto_nombre, categoria_id):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET categoria_id = ? WHERE nombre = ?", (categoria_id, producto_nombre))
    conn.commit()
    conn.close()
    console.print("[bold green]Producto agregado a la categoría exitosamente.[/bold green]")

def eliminar_producto_de_categoria(producto_nombre):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET categoria_id = NULL WHERE nombre = ?", (producto_nombre,))
    conn.commit()
    conn.close()
    console.print("[bold green]Producto eliminado de la categoría exitosamente.[/bold green]")

def agregar_producto_a_proveedor(producto_nombre, proveedor_id):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET proveedor_id = ? WHERE nombre = ?", (proveedor_id, producto_nombre))
    conn.commit()
    conn.close()
    console.print("[bold green]Producto agregado al proveedor exitosamente.[/bold green]")

def eliminar_producto_de_proveedor(producto_nombre):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET proveedor_id = NULL WHERE nombre = ?", (producto_nombre,))
    conn.commit()
    conn.close()
    console.print("[bold green]Producto eliminado del proveedor exitosamente.[/bold green]")

def agregar_producto_a_bodega(producto_nombre, bodega_id):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET bodega_id = ? WHERE nombre = ?", (bodega_id, producto_nombre))
    conn.commit()
    conn.close()
    console.print("[bold green]Producto agregado a la bodega exitosamente.[/bold green]")

def retirar_producto_de_bodega(producto_nombre, cantidad):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Producto SET stock = stock - ? WHERE nombre = ? AND bodega_id IS NOT NULL", (cantidad, producto_nombre))
    conn.commit()
    conn.close()
    console.print("[bold green]Producto retirado de la bodega exitosamente.[/bold green]")

def consultar_disponibilidad_producto_bodega(producto_nombre, bodega_id):
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock
    FROM Producto p
    WHERE p.nombre = ? AND p.bodega_id = ?
    ''', (producto_nombre, bodega_id))
    producto = cursor.fetchone()
    conn.close()
    if producto:
        table = tabulate([producto], headers=['ID', 'Nombre', 'Descripción', 'Precio', 'Stock'], tablefmt='fancy_grid')
        console.print(table)
    else:
        console.print("[bold red]Producto no encontrado en esta bodega.[/bold red]")

def listar_productos():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock, c.nombre AS categoria, pr.nombre AS proveedor, b.nombre AS bodega
    FROM Producto p
    LEFT JOIN Categoria c ON p.categoria_id = c.id
    LEFT JOIN Proveedor pr ON p.proveedor_id = pr.id
    LEFT JOIN Bodega b ON p.bodega_id = b.id
    ''')
    productos = cursor.fetchall()
    conn.close()
    if productos:
        table = tabulate(productos, headers=['ID', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría', 'Proveedor', 'Bodega'], tablefmt='fancy_grid')
        console.print(table)
    else:
        console.print("[bold red]No hay productos registrados.[/bold red]")

def listar_categorias():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, descripcion FROM Categoria')
    categorias = cursor.fetchall()
    conn.close()
    if categorias:
        table = tabulate(categorias, headers=['ID', 'Nombre', 'Descripción'], tablefmt='fancy_grid')
        console.print(table)
    else:
        console.print("[bold red]No hay categorías registradas.[/bold red]")

def listar_proveedores():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, direccion, telefono FROM Proveedor')
    proveedores = cursor.fetchall()
    conn.close()
    if proveedores:
        table = tabulate(proveedores, headers=['ID', 'Nombre', 'Dirección', 'Teléfono'], tablefmt='fancy_grid')
        console.print(table)
    else:
        console.print("[bold red]No hay proveedores registrados.[/bold red]")

def listar_bodegas():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, ubicacion, capacidad_maxima FROM Bodega')
    bodegas = cursor.fetchall()
    conn.close()
    if bodegas:
        table = tabulate(bodegas, headers=['ID', 'Nombre', 'Ubicación', 'Capacidad Máxima'], tablefmt='fancy_grid')
        console.print(table)
    else:
        console.print("[bold red]No hay bodegas registradas.[/bold red]")

def informe_stock_total():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(stock) FROM Producto')
    total_stock = cursor.fetchone()[0]
    conn.close()
    return total_stock

def informe_stock_por_categoria():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.nombre, SUM(p.stock)
    FROM Producto p
    JOIN Categoria c ON p.categoria_id = c.id
    GROUP BY c.nombre
    ''')
    informe = cursor.fetchall()
    conn.close()
    return informe

def informe_stock_por_proveedor():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT pr.nombre, SUM(p.stock)
    FROM Producto p
    JOIN Proveedor pr ON p.proveedor_id = pr.id
    GROUP BY pr.nombre
    ''')
    informe = cursor.fetchall()
    conn.close()
    return informe

def informe_stock_por_bodega():
    conn = sqlite3.connect('GestionInventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT b.nombre, SUM(p.stock)
    FROM Producto p
    JOIN Bodega b ON p.bodega_id = b.id
    GROUP BY b.nombre
    ''')
    informe = cursor.fetchall()
    conn.close()
    return informe

def menu():
    while True:
        console.print("\n[bold blue]Sistema de Gestión de Inventario[/bold blue]")
        console.print("[bold]Registrar los datos para Inventario[/bold]")
        console.print("[green]1.[/green] Agregar Categoría")
        console.print("[green]2.[/green] Agregar Proveedor")
        console.print("[green]3.[/green] Agregar Bodega")
        console.print("[green]4.[/green] Agregar Producto")
        console.print("[green]5.[/green] Eliminar Producto")
        console.print("[bold]Gestion de Stock[/bold]")
        console.print("[green]6.[/green] Agregar Stock")
        console.print("[green]7.[/green] Retirar Stock")
        console.print("[green]8.[/green] Calcular el valor total del stock")
        console.print("[bold]Agregar o Eliminar los datos para Inventario[/bold]")
        console.print("[green]9.[/green] Agregar Producto a Categoría")
        console.print("[green]10.[/green] Eliminar Producto de Categoría")
        console.print("[green]11.[/green] Agregar Producto a Proveedor")
        console.print("[green]12.[/green] Eliminar Producto de Proveedor")
        console.print("[green]13.[/green] Agregar Producto a Bodega")
        console.print("[green]14.[/green] Retirar Producto de Bodega")
        console.print("[green]15.[/green] Consultar Disponibilidad de Producto en Bodega")
        console.print("[bold]Digite el numero para consultar[/bold]")
        console.print("[green]16.[/green] Consultar Producto")
        console.print("[green]17.[/green] Consultar Categoría")
        console.print("[green]18.[/green] Consultar Proveedor")
        console.print("[green]19.[/green] Consultar Bodega")
        console.print("[green]20.[/green] Informe de Stock")
        console.print("[green]21.[/green] Listar Productos")
        console.print("[green]22.[/green] Listar Categorías")
        console.print("[green]23.[/green] Listar Proveedores")
        console.print("[green]24.[/green] Listar Bodegas")
        console.print("[green]25.[/green] Eliminar Todos los Datos")
        console.print("[green]26.[/green] Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            nombre = input("Ingrese el nombre de la categoría: ")
            descripcion = input("Ingrese la descripción de la categoría: ")
            agregar_categoria(nombre, descripcion)
            console.print("[bold green]Categoría agregada exitosamente.[/bold green]")

        elif opcion == '2':
            nombre = input("Ingrese el nombre del proveedor: ")
            direccion = input("Ingrese la dirección del proveedor: ")
            telefono = input("Ingrese el teléfono del proveedor: ")
            productos = input("Ingrese los productos que proporciona el proveedor (separados por coma): ").split(',')
            agregar_proveedor(nombre, direccion, telefono, productos)
            console.print("[bold green]Proveedor agregado exitosamente.[/bold green]")

        elif opcion == '3':
            nombre = input("Ingrese el nombre de la bodega: ")
            ubicacion = input("Ingrese la ubicación de la bodega: ")
            capacidad_maxima = int(input("Ingrese la capacidad máxima de la bodega: "))
            productos = input("Ingrese los productos que almacenará la bodega (separados por coma): ").split(',')
            agregar_bodega(nombre, ubicacion, capacidad_maxima, productos)
            console.print("[bold green]Bodega agregada exitosamente.[/bold green]")

        elif opcion == '4':
            nombre = input("Ingrese el nombre del producto: ")
            descripcion = input("Ingrese la descripción del producto: ")
            precio = float(input("Ingrese el precio del producto: "))
            stock = int(input("Ingrese la cantidad en stock del producto: "))
            categoria_id = int(input("Ingrese el ID de la categoría del producto: "))
            proveedor_id = int(input("Ingrese el ID del proveedor del producto: "))
            bodega_id = int(input("Ingrese el ID de la bodega del producto: "))
            agregar_producto(nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id)
            console.print("[bold green]Producto agregado exitosamente.[/bold green]")

        elif opcion == '5':
            nombre = input("Ingrese el nombre del producto a eliminar: ")
            eliminar_producto(nombre)

        elif opcion == '6':
            nombre_producto = input("Ingrese el nombre del producto al que desea agregar stock: ")
            cantidad = int(input("Ingrese la cantidad de stock a agregar: "))
            agregar_stock(nombre_producto, cantidad)

        elif opcion == '7':
            nombre_producto = input("Ingrese el nombre del producto al que desea retirar stock: ")
            cantidad = int(input("Ingrese la cantidad de stock a retirar: "))
            retirar_stock(nombre_producto, cantidad)

        elif opcion == '8':
            calcular_valor_total_stock()

        elif opcion == '9':
            producto_nombre = input("Ingrese el nombre del producto a agregar a la categoría: ")
            categoria_id = int(input("Ingrese el ID de la categoría: "))
            agregar_producto_a_categoria(producto_nombre, categoria_id)

        elif opcion == '10':
            producto_nombre = input("Ingrese el nombre del producto a eliminar de la categoría: ")
            eliminar_producto_de_categoria(producto_nombre)

        elif opcion == '11':
            producto_nombre = input("Ingrese el nombre del producto a agregar al proveedor: ")
            proveedor_id = int(input("Ingrese el ID del proveedor: "))
            agregar_producto_a_proveedor(producto_nombre, proveedor_id)

        elif opcion == '12':
            producto_nombre = input("Ingrese el nombre del producto a eliminar del proveedor: ")
            eliminar_producto_de_proveedor(producto_nombre)

        elif opcion == '13':
            producto_nombre = input("Ingrese el nombre del producto a agregar a la bodega: ")
            bodega_id = int(input("Ingrese el ID de la bodega: "))
            agregar_producto_a_bodega(producto_nombre, bodega_id)

        elif opcion == '14':
            producto_nombre = input("Ingrese el nombre del producto a retirar de la bodega: ")
            cantidad = int(input("Ingrese la cantidad a retirar: "))
            retirar_producto_de_bodega(producto_nombre, cantidad)

        elif opcion == '15':
            producto_nombre = input("Ingrese el nombre del producto a consultar en la bodega: ")
            bodega_id = int(input("Ingrese el ID de la bodega: "))
            consultar_disponibilidad_producto_bodega(producto_nombre, bodega_id)

        elif opcion == '16':
            nombre = input("Ingrese el nombre del producto a consultar: ")
            consultar_producto(nombre)

        elif opcion == '17':
            nombre = input("Ingrese el nombre de la categoría a consultar: ")
            consultar_categoria(nombre)

        elif opcion == '18':
            nombre = input("Ingrese el nombre del proveedor a consultar: ")
            consultar_proveedor(nombre)

        elif opcion == '19':
            nombre = input("Ingrese el nombre de la bodega a consultar: ")
            consultar_bodega(nombre)

        elif opcion == '20':
            console.print("Seleccione el tipo de informe de stock:", style="bold yellow")
            console.print("[green]1.[/green] Stock Total")
            console.print("[green]2.[/green] Stock por Categoría")
            console.print("[green]3.[/green] Stock por Proveedor")
            console.print("[green]4.[/green] Stock por Bodega")

            tipo_informe = input("Seleccione una opción: ", )

            if tipo_informe == '1':
                console.print("Stock total:", informe_stock_total())
            elif tipo_informe == '2':
                informe = informe_stock_por_categoria()
                for categoria, stock in informe:
                    console.print(f"{categoria}: {stock}")
            elif tipo_informe == '3':
                informe = informe_stock_por_proveedor()
                for proveedor, stock in informe:
                    console.print(f"{proveedor}: {stock}")
            elif tipo_informe == '4':
                informe = informe_stock_por_bodega()
                for bodega, stock in informe:
                    console.print(f"{bodega}: {stock}")
            else:
                console.print("Opción no válida.", style="bold red")

        elif opcion == '21':
            listar_productos()

        elif opcion == '22':
            listar_categorias()

        elif opcion == '23':
            listar_proveedores()

        elif opcion == '24':
            listar_bodegas()

        elif opcion == '25':
            confirmar = input("¿Está seguro de que desea eliminar todos los datos? Esta acción no se puede deshacer. (s/n): ")
            if confirmar.lower() == 's':
                conn = sqlite3.connect('GestionInventario.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Producto")
                cursor.execute("DELETE FROM Categoria")
                cursor.execute("DELETE FROM Proveedor")
                cursor.execute("DELETE FROM Bodega")
                conn.commit()
                conn.close()
                console.print("[bold green]Todos los datos han sido eliminados exitosamente.[/bold green]")

        elif opcion == '26':
            console.print("[bold green]Saliendo del sistema...[/bold green]")
            break

        else:
            console.print("[bold red]Opción no válida. Por favor, seleccione una opción del menú.[/bold red]")

menu()
