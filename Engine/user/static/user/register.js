import {
  element,
  elements,
  eyeToggle,
  makeToastNotification
} from '../../../static/helper.js';

eyeToggle(
  element('#password-icon-container'),
  element('#password'),
  element('#eye'),
  element('#eye-slash')
);

/**
 * Validate elements and update their color based on the validation results.
 * @param {HTMLElement} inputElementSelector - The selector used to target the input element.
 * @param {Array<{ validate: Function, message: string }>} validations - Array of validation objects with `validate` and `message` properties.
 * @param {string} [successColor='green'] - The color to apply if all validations pass.
 * @return {boolean} If the validations encountered any errors.
 */
function runValidations(inputElementSelector, validations) {
  /** @const {string} */
  const errorColor = 'red';

  /** @const {string} */
  const successColor = 'green';

  /** @type {HTMLElement} */
  const inputElement = element(inputElementSelector);

  /** @type {string} */
  const value = inputElement.value.trim();

  /** @type {HTMLElement} */
  const inputElementIcon = inputElement.closest('svg');

  /** @type {HTMLElement} */
  const elementForColor = inputElementIcon ? inputElementIcon : inputElement;

  for (const rule of validations) {
    /** @type {boolean} */
    const isValid = rule.validate(value);

    /** @type {string} */
    const message = rule.message;

    if (!isValid) {
      elementForColor.style.fill = errorColor;
      makeToastNotification(message);
      return false;
    }
  }

  elementForColor.style.fill = successColor;
  return true;
}

/** @type {boolean} */
let stillHasErrors = true;

/**
 * Validate the username input element.
 * @return {boolean} Whether the username validation passed or not.
 */
function validateUsername() {
  return runValidations('#username', [
    {
      validate: value => value.length > 2,
      message: 'Username should have at least 3 characters.'
    },
    {
      validate: value => value.length < 30,
      message: 'Username should have at most 30 characters.'
    },
    {
      validate: value => value !== '',
      message: 'Username should not be empty.'
    }
  ]);
}

/**
 * Validate the email input element.
 * @return {boolean} Whether the email validation passed or not.
 */
function validateRegister() {
  return runValidations('#email', [
    {
      validate: value => value.match(/[@]/) !== null,
      message: 'Missing @'
    },
    {
      validate: value => value.match('.com') !== null,
      message: 'Missing .com'
    },
    {
      validate: value => value !== '',
      message: 'Email cannot be empty.'
    }
  ]);
}

/**
 * Validate the password input element.
 * @return {boolean} Whether the password validation passed or not.
 */
function validatePassword() {
  return runValidations('#password', [
    {
      validate: value => value.match(/[0-9]/) !== null,
      message: 'Password should contain at least one number.'
    },
    {
      validate: value => value.match(/[!@#$%^&*()_+}{":?></*+[;'./,]/) !== null,
      message: 'Password should contain at least one special character.'
    }
  ]);
}

/**
 * Validate the form based on the target element or all fields if no target is provided.
 * @param {HTMLElement} [targetElement] - The specific element to validate, or undefined to validate all fields.
 */
function validateForm(targetElement) {
  if (!targetElement) {
    stillHasErrors = [
      validatePassword(),
      validateRegister(),
      validateUsername()
    ].some(validation => validation === false);
    return;
  }

  if (targetElement.id === 'password') {
    stillHasErrors = validatePassword();
  }

  if (targetElement.id === 'register-email') {
    stillHasErrors = validateRegister();
  }

  if (targetElement.id === 'username') {
    stillHasErrors = validateUsername();
  }
}

/** @const {number} */
const intervalId = setInterval(() => {
  /** @type {NodeListOf<HTMLElement>} */
  const filledElements = elements('input:-webkit-autofill');

  if (filledElements.length > 0) {
    clearInterval(intervalId);
    validateForm();
  }
}, 100);

/** @type {HTMLFormElement} */
const registrationForm = element('.authentication--form');

/** @param {Event} event - The input event triggered on the form. */
registrationForm.oninput = event => {
  if (event.target.matches('input')) {
    validateForm(event.target);
  }
};

/** @param {Event} event - The click event triggered on the register button. */
registrationForm.onsubmit = event => {
  event.preventDefault();
  validateForm();

  if (stillHasErrors) {
    return;
  }

  /** @type {FormData} */
  const formData = new FormData(registrationForm);

  fetch(registrationForm.dataset.route, {
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

