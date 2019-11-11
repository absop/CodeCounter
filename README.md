[![License][license-image]](/LICENSE)
[![Downloads][packagecontrol-image]][packagecontrol-link]

# CodeCounter
[中文](Chinese.md)


## What is this plugin for?

This is a plugin written for **Sublime Text**, its jobs as its name suggests.


## How to install?
Download the repository and unzip it into your packages path of Sublime Text, or direct clone it with the help of `git` tools.

Of course, you can also use `Package Control` to help you if you have installed it before.


## Features overview
- three `sidebar Menu items`
    * Files Size
    * Code Counter
    * Code Counter Filtered

- two practical `commands`
    * CodeCounter: count dir
    * CodeCounter: count dir filtered


## Usage
Sidebar menu items are suitable for folders that have been mounted in the sidebar and for people who like to use a mouse.
Enter <kbd>ctrl+shift+p</kbd> to show a `command_palette` to input and run `sublime-commands` is considered a very powerful and convenient feature of Sublime Text.

- Sidebar menu items' feature explaination
    * `Files Size` will count the size of that folder or file, the result is highlighting shown in a `Panel` as below.
      ![Files size](image/files_size.png)

    * `Code Counter` shows you some statistic infomation of that folder. counting result is shown in a `View` as below.
      ![Overview](image/overview.png)

    * `Code Counter Filtered` is like `Code Counter`, but will request you to input a list of `pattern`(More on that later) before it works.

- commands' feature explaination
    * `CodeCounter: count dir` asks you to input a file path exists in you OS, then do the same job of `Code Counter`.
    * `CodeCounter: count dir filtered` asks you to input a file path exists in you OS, then do the same job of `Code Counter Filtered`.

### View operations
In a overview view, double-clicking a language name will open a new *View* to show the detail statistic result of that language, you can also move cursor into the name region of the language you want to know more about, then press down <kbd>d</kbd> or <kbd>enter</kbd> to view it. We call the new entered view as `detail view`, it look like this.
![Detail](image/detail.png)

In a `detail view`, double-clicking file paths will open their corresponding file. hotkeys <kbd>o</kbd> and <kbd>enter</kbd> can also help you doing jobs.


## Pattern inputting
Pattern is used to filter files that you do not wish them appear in the result.
Files whose absolute path contains the pattern will not be counted in the result.

### Example
Consider there a directory structure as below
```
/root/a/...
     /b/...
     /c/...
     /d.txt
```
You want to count code under the directory `root` but don't want the `b` subdirctory is counted in, so you want to input a pattern to rule out it, `Code Counter Filtered` can help you doing this.

After you have buttoned down the menu item `Code Counter Filtered` or entered command `CodeCounter: count dir filtered` and inputed a file path, the plugin will ask you to input a pattern, you shoud input a pattern `/b/`(On all platforms) or `\b\`(On windows) to achieve your goal. If you want to exclude `/b/` and `d.txt`, consider input `/b/;d.txt`.

### Pattern specific
Some characters are escaped to generate a appropriate regular expression.
- `;` is used to separate patterns, can be replaced by a `|` character.
- `*` is considered as `.*` in a regular expression.
- `file.ext` just `file.ext`.


## Settings
```json
{
    "encoding": "utf-8",
}
```
Please set a right `encoding` to recognize paths on your OS properly.

Other settings
```json
{
    "extensions": {
        "language's name": ["language's extensions1", ]
    },

    "fullnames": {
        "Make" : ["Makefile" , ]
    }
}
```


## Problems

- double-clicking language names will always create a new view, even if there is same one has exists.

- In a `Overview` view, after you have double-clicked a language name and got into a new view, back into the `Overview` view, you will meet some problems of moving cursor by keyboard. I think this is probably a little bug of **Sublime Text** itself. If you have more knowledge about this, please let me know (zlang0@163.com), thanks!

[Issue](https://github.com/absop/CodeCounter/issues)


[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[packagecontrol-image]: https://img.shields.io/packagecontrol/dt/CodeCounter.svg
[packagecontrol-link]: https://packagecontrol.io/packages/CodeCounter
