/* global FileReader, Papa, Handsontable, Base64 */

function disableButtons() {
  disableButton('save');
  disableButton('load');
}

function enableButtons() {
  enableButton('save');
  enableButton('load');
}

function onSaveSuccess(response) {
  showSuccess('save', response);
}

function onSaveError(response) {
  showError('save', response);
}

function onLoadSuccess(response) {
  showSuccess('load', response);
}

function onLoadError(response) {
  showError('load', response);
}

function onDataChange(changes) {
  clearResult('save');
  clearResult('load');
}

function exportAsString(table) {
  var surroundWithQuotes = function (string) {
    return '"' + string + '"';
  }

  var joinWithComma = function (array) {
    return array.map(surroundWithQuotes).join(',');
  }

  var data = [table.getColHeader()].concat(table.getData());
  var result = data.map(joinWithComma).join('\n') + '\n';

  return result;
}

function renderTable(resource, config) {
  var handsontableTable = {};
  var url = resource + '/retrieve';
  var tableContainer = $('#handsontable-container').get(0);

  tableContainer.innerHTML = '';
  tableContainer.className = '';

  Papa.parse(url, {
    download: true,
    header: true,
    quoteChar: '"',
    skipEmptyLines: true,
    complete: function (results) {
      var defaultConfig = {
        data: results.data,
        rowHeaders: true,
        columnSorting: true,
        contextMenu: true,
        afterChange: onDataChange
      }
      handsontableTable = new Handsontable(
        tableContainer,
        $.extend(true, defaultConfig, config)
      );
    }
  });

  $('#data-save').submit(function(e) {
    e.preventDefault();

    disableButtons();
    clearResult('save');
    showSpinner('save');

    var data = exportAsString(handsontableTable);
    var content = Base64.encode(data);

    $.ajax({
      url: resource + '/save',
      method: 'POST',
      data: {
        content: content,
      },
      success: onSaveSuccess,
      error: onSaveError,
      complete: enableButtons
    });
  });

  $('#data-load').submit(function(e) {
    e.preventDefault();

    disableButtons();
    clearResult('load');
    showSpinner('load');

    $.ajax({
      url: resource + '/load',
      success: onLoadSuccess,
      error: onLoadError,
      complete: enableButtons
    });
  });
}
