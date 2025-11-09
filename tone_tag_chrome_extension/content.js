console.log('content.js loaded');
    const cb = document.getElementById('checkcheck');
    //this saves suggestions to chrome storage and retrives it bc chrome was throwing a fit whats new
let suggestionsEnabled = true;
if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync && chrome.storage.sync.get) {
  chrome.storage.sync.get('suggestionsEnabled', ({ suggestionsEnabled: val }) => {
    suggestionsEnabled = typeof val === 'boolean' ? val : true;
    console.log('content.js: initial suggestionsEnabled =', suggestionsEnabled);
  });
  if (chrome.storage.onChanged && typeof chrome.storage.onChanged.addListener === 'function') {
    chrome.storage.onChanged.addListener((changes, area) => {
      if (area === 'sync' && changes.suggestionsEnabled) {
        suggestionsEnabled = changes.suggestionsEnabled.newValue;
        console.log('content.js: suggestionsEnabled changed ->', suggestionsEnabled);
      }
    });
  }
}
(function initPopupIfPresent() {
  //if the popup is real do popup things lol
  try {
    if (!cb) return;
    //popup stuffs
    const textInput = document.getElementById('sentence');
    const analyzeButton = document.getElementById('analyzeButton');
    const resultParagraph = document.getElementById('result');
    //more chrome temper tantrum handling
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync && chrome.storage.sync.get) {
      chrome.storage.sync.get('suggestionsEnabled', ({ suggestionsEnabled }) => {
        cb.checked = typeof suggestionsEnabled === 'boolean' ? suggestionsEnabled : true;
      });
    }
    cb.addEventListener('change', () => { //checks for changes and saves it to chrome, would be relevant if I could get the highlights to work
      const enabled = cb.checked;
      console.log(enabled ? 'Suggestions Enabled' : 'Suggestions Disabled');
      try {
        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync && chrome.storage.sync.set) {
          chrome.storage.sync.set({ suggestionsEnabled: enabled });
        }
      } catch (e) {
        console.error('err setting suggestionsEnabled', e);
      }
    });

    // The actual fun stuff but not ML :(((
    if (analyzeButton) {
      analyzeButton.addEventListener('click', () => {
        const text = (textInput && textInput.value) ? textInput.value.trim() : '';
        if (!text) {
          if (resultParagraph) resultParagraph.textContent = 'Result: Please enter a sentence.';
          return;
        }
        // temporary placeholder bc tensorflowjs stinky
        if (resultParagraph) resultParagraph.textContent = 'Result: /neu';
      });
    }
  } catch (e) {
    console.error('Popup init error', e);
  }
})();