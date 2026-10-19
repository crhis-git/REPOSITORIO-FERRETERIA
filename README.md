Sistema de Mesa de Partes — Ferretería Lázaro
Prototipo de consola en Python para centralizar el registro y seguimiento de documentos de proveedores. Se organiza por módulos y conserva los datos localmente en SQLite.
Requisitos
Python 3.10 o superior recomendado.
No necesita instalar librerías externas: usa la biblioteca estándar de Python.
Ejecutar con datos ficticios de demostración
Para probar las funciones desde el primer inicio, abre una terminal en esta carpeta y ejecuta estos comandos en orden:
```bash
python datos_prueba.py
python main.py
```
En Windows también puedes usar:
```powershell
py datos_prueba.py
py main.py
```
La primera orden carga 10 proveedores y 25 documentos ficticios; la segunda inicia el menú del sistema. La base de datos se guarda en `data/mesa_partes.db`.
La carga de pruebas es opcional e idempotente: añade los registros que falten, no borra ni sobrescribe registros existentes y no duplica documentos si ejecutas el comando más de una vez. Incluye distintos estados, áreas, fechas límite vencidas, próximas y sin fecha, además de historiales para probar búsquedas, ordenamientos, reportes y alertas. Todos los datos identificativos son inventados.
Ejecutar sin datos precargados
Si deseas usar una base vacía, ejecuta solamente:
```bash
python main.py
```
En Windows: `py main.py`.
Pruebas automáticas
```bash
python -m unittest discover -s tests -v
```
Funciones incluidas
Registrar proveedores (código, razón social, RUC, teléfono, correo y dirección).
Registrar documentos con número de registro automático, fechas, asunto, área y referencia digital.
Validar campos obligatorios, fechas y referencias a proveedores existentes.
Consultar por búsqueda binaria (número de registro) o búsqueda lineal (texto).
Ordenar por fecha mediante Bubble Sort y por código de proveedor mediante Insertion Sort.
Actualizar estado y observaciones; guardar cada acción en el historial.
Archivar documentos y bloquear la edición directa de documentos archivados.
Reportar matriz de área por estado.
Mostrar alertas de documentos pendientes, próximos a vencer, que vencen hoy o vencidos.
Estructura del proyecto
```text
MesaDePartesFerreteriaLazaro/
├── main.py
├── database.py
├── proveedores.py
├── documentos.py
├── validaciones.py
├── datos_prueba.py
├── tests/
│   └── test_sistema.py
├── data/
│   └── .gitkeep
├── .gitignore
└── README.md
```
Notas de diseño
`main.py`: menú e interacción por consola.
`proveedores.py`: registro y consulta de proveedores.
`documentos.py`: documentos, búsquedas, ordenamientos, estados, historial, matriz y alertas.
`validaciones.py`: validaciones reutilizables.
`database.py`: esquema y conexión SQLite.
`datos_prueba.py`: carga manual de 10 proveedores y 25 documentos ficticios para pruebas integrales.
`tests/test_sistema.py`: pruebas automatizadas aisladas con una base temporal.
`.gitignore`: evita subir caché, entornos virtuales y la base de datos local.
Subir a GitHub
```bash
git init
git add .
git commit -m "Implementa sistema de mesa de partes en Python"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git push -u origin main
```
Si ya clonaste un repositorio, no vuelvas a ejecutar `git init` ni `git remote add origin`; revisa el remoto con `git remote -v`.
Alcance académico
La propuesta conserva las operaciones del seudocódigo original y las amplía según el informe: datos de contacto del proveedor, fecha límite, historial de acciones, persistencia SQLite, matriz Área × Estado y alertas. Es un prototipo local de consola, no una aplicación web multiusuario.
