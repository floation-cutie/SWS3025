function testOverSpeed () {
    // 获取x, y, z轴的加速度值
    x = input.acceleration(Dimension.X)
    y = input.acceleration(Dimension.Y)
    z = input.acceleration(Dimension.Z)
    // 获取倾角
    pitch = input.rotation(Rotation.Pitch)
    roll = input.rotation(Rotation.Roll)
    // 计算总加速度
    totalAcceleration = Math.sqrt(x * x + y * y + z * z)
    // 设置阈值，这里示例使用1000mg（约1g）作为跌倒检测阈值
    // basic.showIcon(IconNames.Happy)
    testAngle()
    if (totalAcceleration > 3000 || flat) {
        // 显示悲伤表情
        basic.showIcon(IconNames.Sad)
        // 通过radio通信
        radio.sendString("Fall Down")
        for (let index = 0; index < 3; index++) {
            music.play(music.tonePlayable(494, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        }
        // 发送信号
        basic.pause(1000)
        basic.clearScreen()
    }
}

input.onButtonPressed(Button.A, function () {
    radio.sendString("Voice assistant")
    basic.showIcon(IconNames.Giraffe)
})
input.onButtonPressed(Button.B, function () {
    radio.sendString("Emergency")
    basic.showLeds(`
        . . # . .
        . . # . .
        . . # . .
        . . . . .
        . . # . .
        `)
})
function testAngle () {
    pitch = input.rotation(Rotation.Pitch)
    roll = input.rotation(Rotation.Roll)
    if (Math.abs(pitch) < 10 && Math.abs(roll) < 10) {
        flat = true
    } else {
        flat = false
    }
}
let flat = false
let totalAcceleration = 0
let roll = 0
let pitch = 0
let z = 0
let y = 0
let x = 0
radio.setGroup(106)
radio.setTransmitPower(7)
radio.setTransmitSerialNumber(true)
basic.showIcon(IconNames.Yes)
basic.forever(function () {
    testOverSpeed()
    // 每100毫秒检查一次
    basic.pause(100)
})
