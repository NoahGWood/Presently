const Plugin = () => {

    // The reveal.js instance this plugin is attached to
    let deck;
    let audioPlayer;
    let currentAudio;

    function playAudio(){
        audioPlayer.play();
    };

    function changeMP3(newfile) {
        audioPlayer = new Audio(newfile);
        audioPlayer.addEventListener("ended", function() {
            nextClip();
        })
    };

    function nextClip() {
        // Loads the next presentation & audio file

    }

    function getNoteText() {
        var slide = deck.getCurrentSlide()
        var aside = slide.querySelector('aside.notes');
        if (aside != none) {
            // We have text to convert
            return aside.innerText;;
        }
        return none
    }

    function 

    function generateNarration(){
        // Generates a new narration based on note
        var speech = getNoteText();

    }

    return {
        id: 'narrate',
        init: function( reveal ) {
            deck = reveal;
        }

    }
}

export default Plugin;