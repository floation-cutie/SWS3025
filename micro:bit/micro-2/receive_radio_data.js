radio.onReceivedString(function (receivedString) {
    if (receivedString == "Fall Down") {
        serial.writeLine(receivedString)
        basic.showIcon(IconNames.Surprised)
    } else if (receivedString == "Voice assistant") {
        serial.writeLine(receivedString)
        basic.showIcon(IconNames.TShirt)
    } else if (receivedString == "Emergency"){
        serial.writeLine(receivedString)
        basic.showIcon(IconNames.Umbrella)
    } else {
        basic.showIcon(IconNames.Sad)
    }
})
serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    let str = serial.readLine()
    if (str == "response") {
        basic.showIcon(IconNames.Happy)
    } else if (str == "D") {
        music.play(music.tonePlayable(494, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        basic.showString('D')
    } else {
        basic.showIcon(IconNames.Duck)
    }
})
radio.setGroup(106)
radio.setTransmitPower(7)
radio.setTransmitSerialNumber(true)
basic.showIcon(IconNames.Yes)
basic.forever(function () {
	
})
