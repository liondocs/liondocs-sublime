# LionDocs Sublime Text Plugin

This is an LionDocs plugin for Sublime Text.

[Demo](https://www.youtube.com/watch?v=RRPShnY_10E)

## Install

Install `LionDocs` with [Package Control](https://packagecontrol.io) and restart Sublime.

## Configure

Go to `Preferences` -> `Package Settings` -> `LionDocs` -> `Settings`

Your user configuration file should look like this:

```
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

## Use

Plugin functions are executed from the Sublime Text Command Palette.

### Functions

* **Get SHA**: Gets the SHA commit of the current opened file (in translated-content) but in content.
  * **Insert SourceCommit to cursor position**: Inserts the SHA commit in metadata format at the current cursor position.
  * **Copy SourceCommit to clipboard**: Copies the SHA commit to the clipboard.

* **Transfer**: Copies the current opened file (in content) to translated-content in its respective path.

  * **Transfer file**: Copies exactly the same file.

  * **Transfer file + SourceCommit**: Copies the file and adds the respective SHA in metadata format.

## Advice

For now it is being assumed that your directory tree is something similar to the following:

```
mdn/
├─ content/
├─ translated-content/
```

So with different structures it can cause problems. The root does not necessarily have to be *mdn*, but the sub-directories must have the same name and be in the same folder.

Tested in **Windows** and **Ubuntu**
