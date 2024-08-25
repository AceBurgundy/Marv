import {
  element,
  eyeToggle,
  makeToastNotification
} from '../../../static/helper.js';

eyeToggle(
  element('#password-icon-container'),
  element('#password'),
  element('#eye'),
  element('#eye-slash')
);

/** @type {HTMLFormElement} */
const form = element('.authentication--form');

/**
 * Handle form submission to send data via POST request.
 * @param {Event} event - The submit event triggered on the form.
 */
form.onsubmit = event => {
  event.preventDefault();

  /** @type {FormData} */
  const formData = new FormData(form);

  fetch(form.dataset.route, {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(response => {
      if (response.status === 'success' && response.url) {
        window.location.href = response.url;
        return;
      }

      if (response.message) makeToastNotification(response.message);
    })
    .catch(error => {
      console.log(error);
    });
};
