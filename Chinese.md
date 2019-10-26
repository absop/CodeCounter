![License][license-image]


# CodeCounter
[English](README.md)

## 这个插件是做什么用的？
这个插件是为**Sublime Text**编写的, 它的功能正如它的名字所表达的那样（代码 统计）.

## 如何使用？
首先，你需要将这个插件克隆到你的**Sublime Text**的插件目录.
<!-- 当然，如果你安装了**PackageControl**（并且可用：-），推荐使用它来帮你安装。记住插件的名字叫做**CodeCounter** -->
然后, 打开你的**SUblime Text** 并且右键点击一个侧边栏文件夹(如果没有的话就通过快捷键<kbd>alt+p</kbd> 和 <kbd>d</kbd> 添加一个来尝试一下), 你就可以看到两个新的菜单选项了，分别是 `File Size` 和 `Code Counter`。

选择 `File Size` 将会给出关于该文件夹包含的内容的信息, 选择 `Code Counter` 则给出该文件夹的代码统计信息。

代码统计结果首先会以总览的形式显示在一个视图（View）里面，如此如此，
![](image/overview.png)
双击第一列语言名称（或者将光标移到语言名字所在的区域，然后按<kbd>d</kbd>或<kbd>enter</kbd>键），将会打开一个新的视图来显示该语言的详细的代码统计情况，如下。
![](image/detail.png)
在新打开的视图中，会给出每一个代码文件的**大小**、**代码行数**和相对于`ROOTDIR`的**路径**，路径以下划线方式高亮显示，双击这些路径（或者将光标移动到你要打开的文件的路径的区域，然后按<kbd>o</kbd>或<kbd>enter</kbd>键）会打开对应的文件。

## 目前存在的一些问题
- 双击语言名字总是会新建一个视图，即是已经有了一个同样的View。
- 在`Overview`里面，当你双击语言名字之后，再回到`Overview`里面，你会发现不能用键盘来移动光标了。我觉得这很可能是**SublimeText**自己的问题，如果你能明确告诉我，或者你找到了解决这个问题的方法，请告诉我(2913049342@qq.com)，谢谢。

[Issue](https://github.com/absop/CodeCounter/issues)

[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
