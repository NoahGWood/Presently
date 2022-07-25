var wiz1Title = document.getElementById("title");
var wiz2FileButton = document.getElementById("button");
var wiz2FileCancel = document.getElementById("upload-cancel");
var wiz2FileInput = document.getElementById("file");
var wiz2TextBox = document.getElementById("text");
var wiz2text = wiz2TextBox.value;
var wiz4FinalTitle = document.getElementById("final-title");
var wiz4FinalText = document.getElementById("final-text");
var wiz4FileInput = document.getElementById("final-file");
var Wiz4FileLabel = document.getElementById('ff-lbl');
var Wiz4TextLabel = document.getElementById('ft-lbl');
wiz2FileCancel.style.display = "none";

function wiz2ClearText() {
    if (wiz2FileInput.value != ""){
        wiz2text = wiz2TextBox.value;
        wiz2TextBox.value = "";
        wiz2FileButton.value = '...' + wiz2FileInput.value.split('\\')[2]
        wiz2FileCancel.style.display = "inline";
    } else {
        wiz2TextBox.value = wiz2text;
        wiz2FileInput.value = "";
        wiz2FileButton.value = "Upload"
        wiz2FileCancel.style.display = "none";
    }
}

function ClearFile() {
    wiz2FileInput.value=null;
    wiz2ClearText();
}

function Wiz2FileSelector() {
    wiz2FileInput.click();
}

function WizFinal() {
    console.log(wiz1Title.value);
    if (wiz2FileInput.value != "")
    {
        wiz4FileInput.value = wiz2FileInput.value;
        wiz4FileInput.style.display = "block";
        Wiz4FileLabel.style.display = "block";
        wiz4FinalText.style.display = "none";
        Wiz4TextLabel.style.display = "none";
    }
    else{
        wiz4FinalText.value = wiz2TextBox.value;
        wiz4FinalText.style.display = "block";
        Wiz4TextLabel.style.display = "block";
        wiz4FileInput.style.display = "none";
        Wiz4FileLabel.style.display = "none";
    }
    wiz4FinalTitle.value = wiz1Title.value;
}