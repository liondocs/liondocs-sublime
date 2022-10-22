# LionDocs Sublime Text Plugin

This is an LionDocs plugin for Sublime Text.

[Demo](https://www.youtube.com/watch?v=RRPShnY_10E)

## Installation

For now the plugin is not part of the [Package Control](https://packagecontrol.io/) plugin repository so it must be from repository.

But first, a configuration must be added to **Package Control**:

* Go to `Preferences` -> `Package Settings` -> `Package Control` -> `Settings`
* Add `"package_name_map": { "liondocs-sublime": "LionDocs" }`

Now let's install our Plugin

* Open **Command Palette** (`Control or Command + Shift + p`) and select `Add repository`
* Add `https://github.com/liondocs/liondocs-sublime.git` and press Enter
* Open **Command Palette** again, select `Install package` and press Enter
* Search `LionDocs` and Install

Remember, all this is as long as the Plugin is not part of **Package Control** channel.

## Configuration

Go to `Preferences` -> `Package Settings` -> `LionDocs` -> `Settings`

Your user configuration file should look like this:

```jsonc
{
  // Absolute paths to the repositories
  "paths":{
    "content": "",
    "translated-content": ""
  },
  // It must be the same as the one in translated-content
  "lang_code":"",
  // Show alerts in successfully silent operations
  // If False just show message in Sublime Text Console
  "alerts":true
}
```

> **Note:** Silent operations are those that although they are executed correctly, they do not instantly show some sign that they were executed. As for example the transfer of a file.

## Usage

Plugin functions are executed from the Sublime Text context menu.

### Functions

* **Transfer**: Copies the current opened file file in content to translated-content in its respective path.
	* **Same file**: Copies exactly the same file.
	* **With SourceCommit**: Copies the file and adds the respective SHA in metadata format.
* **Get SHA**: Gets the SHA commit of the current opened file but in content.
	* **To cursor position**: Inserts the SHA commit in metadata format at the current cursor position.
	* **To clipboard**: Copies the SHA commit to the clipboard.

## Advice

For now it is being assumed that your directory tree is something similar to the following:

```
mdn/
├─ content/
├─ translated-content/
```

So with different structures it can cause problems. The root does not necessarily have to be *mdn*, but the sub-directories must have the same name and be in the same folder.

Testedin in **Windows** and **Ubuntu**
