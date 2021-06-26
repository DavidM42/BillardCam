const saveCurrentState = async () => {
    try {
        const result = await fetch('/updateFeatures', {
            method: 'post',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
              },
            body: JSON.stringify(featureStates)
        });
        const json = await result.json();
        if (json && json.status === 'Done') {
            alert("Done! Will restart which might take a few seconds");
        }
    } catch(e) {
        console.error(e);
        alert("Error");
    }
};


window.addEventListener('load', () => {
    document.getElementById('saveReload').onclick = saveCurrentState;
});