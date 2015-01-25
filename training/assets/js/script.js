$( document ).ready( function () {
    $('#intro-train-button').click( function () {
        socket.emit('backend', {'event':'start'});
        $('#training-button').addClass('training');
        $('#training-button').text('Stop Training');
        setTimeout(function () {
            $('#buttons-panel').fadeIn(200);   
            $('#go-home-panel').fadeIn(200); 
        }, 200);
        transitionTo('main');
    });
    $('#intro-play-button').click( function () {
        socket.emit('backend', {'event':'play'});
        changeContainerVisibility('person', 'hide');
        $('#go-home-panel').fadeIn(200); 
        $('#bar-container').addClass('bar-container-play');
        transitionTo('main');
    });
    $('#training-button').click( function () {
        var data = {};
        if (!$(this).hasClass('training')) {
            socket.emit('backend', {'event':'start'});
            $(this).addClass('training');
            $(this).text('Stop Training');
        } else {
            socket.emit('backend', {'event':'stop'});
            $(this).removeClass('training');
            $(this).text('Start Training');
        }
    });
    $('#go-home-button').click( function () {
        socket.emit('backend', {'event':'stop'});
        transitionTo('intro');
        $('#buttons-panel').fadeOut(200);   
        $('#go-home-panel').fadeOut(200);
        setTimeout( function () {
            changeContainerVisibility('person', 'show');
            $('#bar-container').removeClass('bar-container-play');
        }, 200);
    });
});

function transitionTo(panel) {
	var id = '#' + panel + '-panel';
	$('.panel').fadeOut(200);
	setTimeout( function () {
		$(id).fadeIn(200);
	}, 200);
}

//Random generator
function getNCommands(num) {
    var commands = ['left', 'baseline', 'right'];
    var tempCommands = [];
    var outCommands = [];
    for (var i = 0; i < num; i++) {
        tempCommands = shuffle(commands);
        outCommands = outCommands.concat(tempCommands);
    }
    console.log(outCommands);
    return outCommands;
}

function armUp(dir) {
    var arm = '#person-arm-' + dir;
    changeLabel(dir);
    if (dir == 'left') {
        $(arm).addClass('move-arm-left');
        setTimeout( function () {
            $(arm).removeClass('move-arm-left');
        }, 2000);
    } else if (dir == 'right') {
        $(arm).addClass('move-arm-right');
        setTimeout( function () {
            $(arm).removeClass('move-arm-right');
        }, 2000);
    }
}

function emitCommand(event, val, dir, thresh, accuracy) {
    if (event == 'pause') {
        setNextDirection(dir);
        transitionTo(event);
    } else if (event == 'state'){
        if (!isVisible('main-panel')) {
            transitionTo('main');    
        }
        moveBarIndicatorTo((val+1)*50);
        renderThreshold((thresh+1)*50);
//            changeContainerVisibility('person', 'show');
//            changeContainerVisibility('bar', 'show');
        if (dir == 'left') {
            armUp('left');
            changeLabel('left');
        } else if (dir == 'right') {
            armUp('right');
            changeLabel('right');
        } else if (dir == 'baseline') {
            changeLabel('baseline');
        }
    } else if (event == 'end') {
        
        transitionTo(event, accuracy*100);
        $(this).removeClass('training');
        $(this).text('Restart Training');
    } else {
        if (accuracy == null) {
            
        } else {
            setAccuracy(event, accuracy);
        }
    }
}

function changeLabel(label) {
    if (label == null) {
        $('#command-label').text('');    
    } else {
        $('#command-label').text(label);    
    }
}

function changeContainerVisibility(name, action) {
    var id = '#' + name + '-container';
    if (action == 'show' && !isVisible(name+'-container')) {
        $(id).fadeIn(300);
    } else if (action == 'hide' && isVisible(name+'-container')) {
        $(id).fadeOut(300);
    }
}

function isVisible(name) {
    return $('#'+name).css('display') != 'none';
}

function startTraining(num) {
    var commandList = getNCommands(num);
    commandList.forEach( function (command, i) {
        setTimeout( function () {
            armUp(command);     
        }, 2500*i);
    });
    setTimeout( function () {
        changeLabel();
    }, 2500*commandList.length);
}

function moveBarIndicatorTo(percentage) {
    if ( percentage < 0 ) {
        percentage = 0;    
    } else if (percentage > 100) {
        percentage = 100;    
    }
    var left = percentage*485/100;
    $('#estimate-indicator').css({'left':left});
}

function renderThreshold(percentage) {
    var dist = percentage*490/100;
    $('#bar-threshold-left').css({'left':dist});
    $('#bar-threshold-right').css({'right':dist});
}

function setNextDirection(dir) {
    $('#next-dir').text(dir);
}
function setAccuracy(panel, accuracy) {
    var id = '#' + panel + '-accuracy';
    $(id).text(Math.round(accuracy) + '%');   
    if (panel == 'classifying') {
        if (accuracy == null) {
            $('#classifying-accuracy-label').hide();    
        } else {
            $('#classifying-accuracy-container').show();    
        }
    }
}