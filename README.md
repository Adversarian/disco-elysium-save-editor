# Disco Elysium Save Editor
A fairly easy Logic check should reveal the function of this repository from its slug.

This tool provides facilities for altering the following:
- ~~Your mind~~
- **Door States**: Open or close locked doors.
- **Resource Values**: Skill points, Health consumables, Morale consumables, Money.
- **Character Sheet Stats**: Intellect, Psyche, Physique and Motorics caps and base stats.
- **Thoughts**: Change the state of all *unknown* and *forgotten* thoughts to *known*, ready to be internalized.
- **In-game Time**: Change the in-game time.

*Altering some of these values may break your tasks. I haven't tested everything. Make backups (even though this already does that for you) and use at your own discretion.*

If you're looking for a specific feature, feel to submit an [issue](https://github.com/Adversarian/disco-elysium-save-editor/issues) or if you can read this absolute mess of a code and do it yourself, a [PR](https://github.com/Adversarian/disco-elysium-save-editor/pulls). There's a fairly decent chance I won't get around to implementing it but at least you can take comfort in the fact that you have done your due diligence.

# Usage

## GUI (Recommended)
The editor features a PyQt6-based GUI with authentic Disco Elysium styling:

```bash
cd src
python gui_editor.py
```

## Executable
Alternatively, download the executable from the latest release and run it. This ain't your first rodeo.

**Note**: *Your AV is probably going to throw a false-positive at the EXE file. I'm not sure how to fix it yet but it seems to be an inherent issue with Python compilers. Rest assured however that the EXE is virus free (to the best of my knowledge). However, if you're still not comfortable with this, you can follow the steps below to build the project yourself (or y'know, just run it on Python since you already need to have it installed to build the executable with [Nuitka](https://nuitka.net/)).*

# Build (on Windows)
## 0. Roll 2D6 and pass a trivial perception check (7) with a (+6) modifier.
[Dice Roll](https://www.google.com/search?q=2d6)
## 1. Clone the repo
```cmd
> git clone https://github.com/Adversarian/disco-elysium-save-editor
```
## 2. Install Nuitka
```cmd
> pip install nuitka
```
## 3. And then the requirements (someone probably should make a requirements-dev.txt so that you don't have to do 2 steps for requirements)
```cmd
> cd disco-elysium-save-editor
> pip install -r requirements.txt
```
## 4. Run `nuitka-build.ps1` to build the executable with Nuitka.
```cmd
> .\nuitka-build.ps1
```

# To Do
- I don't know what to do.
- Fix README (soon™)
- More features (soon™™)

# Wouldn't this be like, a bazillion times easier in C#
Absolutely.

# Then wh-
Because C# stinks.
