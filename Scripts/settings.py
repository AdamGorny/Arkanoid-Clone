windowWidth = 1280
windowHeight = 720

blockLayout = [
    "6666666666666666",
    "5555555555555555",
    "4444444444444444",
    "3333333333333333",
    "2222222222222222",
    "1111111111111111",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                "
]

colorDict = {
    "1" : "green",
    "2" : "yellow",
    "3" : "orange",
    "4" : "red",
    "5" : "purple",
    "6" : "grey",
    "7" : "bronze"
}

blockGap = 2
blockHeight = windowHeight / len(blockLayout) - blockGap
blockWidth = windowWidth / len(blockLayout[0]) - blockGap
topOffset = windowHeight // 40
upgrades = ["contract", "laser", "stretch", "speed"]