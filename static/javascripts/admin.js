function getButton(button_name) {
  var button_selector = '#data-' + button_name + ' button[type="submit"]';
  return $(button_selector);
}

function getOutput(output_name) {
  var output_selector = '#data-' + output_name + '-output';
  return $(output_selector).find('.output');
}

function getSpinner(spinner_name) {
  var spinner_selector = '#data-' + spinner_name + '-output';
  return $(spinner_selector).find('.loading');
}

function showSpinner(spinner_name) {
  var spinner = getSpinner(spinner_name);
  spinner.show();
  spinner.parent().show();
}

function hideSpinner(spinner_name) {
  var spinner = getSpinner(spinner_name);
  spinner.hide();
  spinner.parent().hide();
}

function disableButton(button_name) {
  var button = getButton(button_name);
  button.attr('disabled', true).children('.glyphicon').removeClass('hide');
}

function enableButton(button_name) {
  var button = getButton(button_name);
  button.attr('disabled', false).children('.glyphicon').addClass('hide');
}

function showResult(command_name, command_message) {
  var spinner_name = output_name = command_name;

  var output = getOutput(output_name);

  hideSpinner(spinner_name);

  if (command_message) {
    output.html(command_message);
    output.show();
    output.parent().show();
  }
}

function clearResult(command_name) {
  var output_name = command_name;
  var output = getOutput(output_name);

  output.html('');
  output.hide();
  output.parent().hide();
}

function showSuccess(command_name, command_response) {
  // El firewall del entorno de Madrid intercepta las peticiones a nuestro servidor de forma ocasional,
  // devolviendo una página HTML con código 200, como si todo fuera correcto. Tenemos que comprobar
  // el contenido devuelto para asegurarnos que de verdad la llamada ha tenido éxito.
  if (command_response.includes('<!DOCTYPE html>')) {
    showError(command_name, {
      responseJSON: {
        message: 'No se ha podido conectar con el servidor: <br>'+command_response
      }
    })
  } else {
    showResult(command_name, command_response.message);
  }
}

function showError(command_name, command_response) {
  var message = (command_response.responseJSON && command_response.responseJSON.message);

  if (!message) {
    message = "Se ha producido un error inesperado. <pre>" + command_response.responseText + "</pre>";
  }

  showResult(command_name, message);
}
