function handleClick(toggle) {
    // change featureState Object for this key to new checked status of
    featureStates[toggle.currentTarget.name] = toggle.currentTarget.checked;

    // failed experiment for nested targets via name path split by ::
    // const path = toggle.currentTarget.name.split('::');
    
    // // TODO fix these nested toggle things
    // let element = featureStates[path[0]];
    // for (let i = 1; i < path.length; i++) {
    //     element = element[path[i]];
    // }

    // element = toggle.currentTarget.checked;
}

const loopObjectAppendToggles = (loopObject, beforeHook) => { //namePrefix
    Object.entries(loopObject).forEach((entry) => {
        const key = entry[0];
        const value = entry[1];

        if (Object.entries(value).length > 0) {
            // value is not boolean itself but nested object with sub properties so loop that
            loopObjectAppendToggles(value, beforeHook) //, key);
        } else {
            // let path = key;
            // if (namePrefix) {
            //     path = namePrefix + '::' + path;
            // }

            const label = document.createElement('label');
            label.htmlFor = key;
            label.innerText = key;
    
            // setup inbut toggle checkbox with event handler and all that
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.classList.add('toggle');
            input.name = key;
            input.checked = value;
            // input.onclick = 'handleClick(this);';
            input.onclick = handleClick;
    
            // and append to dom just before hook
            beforeHook.before(label);
            beforeHook.before(input);
        }
    });
}


const initForm = () => {
    const beforeHook = document.getElementById('formBeforeHook');
    loopObjectAppendToggles(featureStates, beforeHook);
};




window.addEventListener('load', () => initForm());