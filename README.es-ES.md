

# Editor de Partidas de Disco Elysium
Una prueba de Lógica bastante sencilla debería revelar la función de este repositorio por su nombre.

Esta herramienta ofrece facilidades para alterar lo siguiente:
- ~~Tu mente~~
- **Estados de las puertas**: Abrir o cerrar puertas bloqueadas.
- **Valores de recursos**: Puntos de habilidad, consumibles de Salud, consumibles de Moral, Dinero.
- **Estadísticas de la ficha**: Límites y valores base de Inteligencia, Psique, Físico y Motricidad.
- **Pensamientos**: Cambiar el estado de todos los pensamientos *desconocidos* y *olvidados* a *conocidos*, listos para ser internalizados.
- **Tiempo en el juego**: Cambiar el tiempo dentro del juego.

*Alterar algunos de estos valores podría romper tus misiones. No he probado todo. Haz copias de seguridad (aunque esto ya lo hace por ti) y úsalo bajo tu propia responsabilidad.*

Si buscas una función específica, siéntete libre de enviar un [issue](https://github.com/Adversarian/disco-elysium-save-editor/issues) o, si puedes leer este completo desorden de código y hacerlo tú mismo, una [PR](https://github.com/Adversarian/disco-elysium-save-editor/pulls). Hay una probabilidad bastante alta de que no llegue a implementarlo, pero al menos puedes estar tranquilo sabiendo que has cumplido con tu parte.

# Uso

## GUI (Recomendado)
El editor cuenta con una GUI basada en PyQt6 con un estilo auténtico de Disco Elysium:

```bash
cd src
python gui_editor.py
```

## Ejecutable
Alternativamente, descarga el ejecutable desde la última versión y ejecútalo. Esta no es tu primera vez en un rodeo.

**Nota**: *Es muy probable que tu antivirus lance un falso positivo con el archivo EXE. No estoy seguro de cómo solucionarlo aún, pero parece ser un problema inherente a los compiladores de Python. Sin embargo, descansa tranquilo: el EXE está libre de virus (por lo que sé). Si aún así no te sientes cómodo con esto, puedes seguir los pasos a continuación para compilar el proyecto tú mismo (o, ya sabes, simplemente ejecutarlo en Python, dado que de todos modos necesitas tenerlo instalado para crear el ejecutable con [Nuitka](https://nuitka.net/)).*

# Compilación (en Windows)
## 0. Lanza 2D6 y supera una comprobación trivial de Percepción (7) con un modificador (+6).
[Dice Roll](https://www.google.com/search?q=2d6)
## 1. Clona el repositorio
```cmd
> git clone https://github.com/Adversarian/disco-elysium-save-editor
```
## 2. Instala Nuitka
```cmd
> pip install nuitka
```
## 3. Y luego los requisitos (alguien debería hacer un requirements-dev.txt para que no tengas que hacer 2 pasos para los requisitos)
```cmd
> cd disco-elysium-save-editor
> pip install -r requirements.txt
```
## 4. Ejecuta `nuitka-build.ps1` para compilar el ejecutable con Nuitka.
```cmd
> .\nuitka-build.ps1
```

# Por hacer
- No sé qué poner.
- Arreglar el README (pronto™)
- Más características (pronto™™)

# ¿No sería esto, como, mil millones de veces más fácil en C#
Absolutamente.

# Entonces, pe-
Porque C# apesta.
