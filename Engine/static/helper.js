/**
 * Selects the first element within the document that matches the specified CSS class selector.
 *
 * @param {string} className - The CSS class selector to match.
 * @returns {Element} - The first Element within the document
 * that matches the specified selector, or null if no matches are found.
 */
export const element = className => document.querySelector(className);

/**
 * Selects all elements within the document that match the specified CSS class selector.
 *
 * @param {string} className - The CSS class selector to match.
 * @returns {NodeListOf<Element>} - A NodeList containing all elements
 * that match the specified selector.
 */
export const elements = className => document.querySelectorAll(className);

/**
 * Adds a character counter to an input field and updates a corresponding counter element.
 * @param {HTMLElement} inputElement - The input field.
 * @param {HTMLElement} counterElement - The counter element.
 * @param {number|null} restriction - The character limit (null for no limit).
 */
export const counter = (inputElement, counterElement, restriction = null) => {
  const updateCounter = () => {
    const { length } = inputElement.value;
    counterElement.children[0].textContent = length;
  };

  input.oninput = () => {
    if (restriction === null || inputElement.value.length <= restriction) {
      updateCounter();
    }
  };

  window.onload = () => updateCounter();
};

/**
 * Toggles the visibility of eye icons and input field type in a form.
 * @param {HTMLElement} eyesContainer - The container for eye icons.
 * @param {HTMLInputElement} input - The input field.
 * @param {HTMLElement} eye - The open eye icon.
 * @param {HTMLElement} eyeSlash - The closed eye icon.
 */
export const eyeToggle = (eyesContainer, input, eye, eyeSlash) => {
  eyesContainer.onclick = () => {
    const isText = input.type === 'text';
    input.type = isText ? 'password' : 'text';
    eye.style.display = isText ? 'none' : 'block';
    eyeSlash.style.display = isText ? 'block' : 'none';
  };
};

/**
 * Displays a toast notification with a message or an array of messages.
 *
 * If a single message is provided, it displays the message as a toast notification.
 * If an array of messages is provided, it displays each message with a 250ms delay between them.
 *
 * @param {string|string[]} messages - A single message or an array of messages to display.
 *
 * @example
 * // Display a single message
 * makeToastNotification('Hello, world!');
 *
 * @example
 * // Display multiple messages with a delay between each
 * makeToastNotification(['First message', 'Second message', 'Third message']);
 */
export function makeToastNotification(messages) {
  const flashes = element('#flashes');

  // Function to show a single message
  function showMessage(message) {
    const newToast = document.createElement('li');
    newToast.classList.add('message');
    newToast.textContent = message;

    flashes.append(newToast);
    newToast.classList.toggle('active');

    setTimeout(() => {
      newToast.classList.remove('active');
      setTimeout(() => newToast.remove(), 500);
    }, 2000);
  }

  // Check if messages is an array
  if (Array.isArray(messages)) {
    // Function to handle array of messages with delay
    async function showMessages(messages) {
      for (let index = 0; index < messages.length; index++) {
        showMessage(messages[index]);
        await new Promise(resolve => setTimeout(resolve, 400)); // Delay between messages
      }
    }

    showMessages(messages);
  } else if (typeof messages === 'string' && messages !== '') {
    showMessage(messages);
  }
}

/**
 * Automatically resizes a textarea element to fit its content.
 */
export const autoResize = element => {
  element.style.height = 'auto';
  element.style.height = `${element.scrollHeight}px`;
};
