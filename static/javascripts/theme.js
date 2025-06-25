// Theme custom js methods
$(document).ready(function(){

  var addChartsAlert = function(selector) {
    var str = {
      'es': 'Datos actualizados a ',
      'en': 'Data up to '
    };
    var dates = {
      '1M.es': '31 de enero de ',
      '1M.en': '31st January ',
      '2M.es': '28 de febrero de ',
      '2M.en': '28th February ',
      '3M.es': '31 de marzo de ',
      '3M.en': '31st March ',
      '4M.es': '30 de abril de ',
      '4M.en': '30th April ',
      '5M.es': '31 de mayo de ',
      '5M.en': '31st Mayo ',
      '6M.es': '30 de junio de ',
      '6M.en': '30th June ',
      '7M.es': '31 de julio de ',
      '7M.en': '31st July ',
      '8M.es': '31 de agosto de ',
      '8M.en': '31st August ',
      '9M.es': '30 de septiembre de ',
      '9M.en': '31st September ',
      '10M.es': '31 de octubre de ',
      '10M.en': '31st October ',
      '11M.es': '30 de noviembre de ',
      '11M.en': '30th November ',
      '12M.es': '31 de diciembre de ',
      '12M.en': '31st December ',
      '.es': '31 de diciembre de ',
      '.en': '31st December ',
    }
    var cont = $(selector);
    if( cont.length > 0 ) {
      var language = $('html').attr('lang');
      var date = dates[last_budget_status+'.'+language];
      if( date != null ) {
        var message = str[language] + date + last_budget_year;
        cont.prepend('<div class="alert alert-data-update">' + message + '</div>');
      }
    }
  };

  var addYearSelectorCustomLabels = function() {
    var extension = {
      'es': 'Prórroga',
      'en': 'Extension',
    };

    $('.data-controllers .layout-slider .slider .slider-tick-label').each(function(){
      var val = $(this).html();
      if (val === '2023'){
        $(this).html(val + '<br/><small><i> ('+ extension[ $('html').attr('lang') ] +')</i></small>');
      }
    });
  };

  // Custom for descriptions in some programmes
  var addCustomDescriptions = function() {
    var descriptionText = {
      'es': '<p>En el año 2013, se llevó a cabo una refinanciación por importe de 333.773.499 € con '+
            'motivo de la subrogación del Ayuntamiento en la posición deudora de la empresa municipal '+
            'Madrid Espacios y Congresos, S.A. y en parte de la deuda de la Empresa Municipal de la '+
            'Vivienda y Suelo, S.A. Este importe, 333,8 millones, no se debe considerar como amortización de 2013 '+
            'ya que no supone una carga real de 2013.</p><p>En el año 2014 se procedió a la refinanciación con '+
            'entidades de crédito privadas del saldo vivo de las operaciones concertadas a través del Fondo estatal '+
            'para la Financiación de los pagos a Proveedores; el importe de tal refinanciación ascendió a '+
            '992.333.741,92 €. Como consecuencia de ello, en los gastos por amortización del año es preciso detraer '+
            'esos 992,3 millones, ya que no suponen carga real de 2014.</p>',
      'en': '<p>In 2013, a refinancing of €333,773,499 was carried out due to the subrogation of the City Council ' +
            'in the debtor position of the municipal company Madrid Espacios y Congresos, S.A. and in part of the debt of the ' +
            'Empresa Municipal de la Vivienda y Suelo, S.A. This amount, 333.8 million, should not be considered as amortization ' +
            'for 2013 since it does not represent a real burden for 2013.</p><p>In 2014, the outstanding balance of the transactions ' +
            'arranged through the state fund Fondo para la Financiación de los pagos a Proveedores was refinanced with private credit ' +
            'institutions; the amount of such refinancing amounted to €992,333,741.92. As a consequence, in the amortization expenses ' +
            'for the year it is necessary to deduct these 992.3 million, since they do not represent a real burden for 2014.</p>'
    }

    var descriptions = {
      '/es/politicas/01': descriptionText.es,
      '/es/programas/01111': descriptionText.es,
      '/en/politicas/01': descriptionText.en,
      '/en/programas/01111': descriptionText.en
    };

    var description = descriptions[ window.location.pathname.substring(0,window.location.pathname.lastIndexOf('/')) ];

    if (description) {
      $('.policies .policies-content .policies-chart').append( '<div class="policy-description">'+description+'</div>' );
    }
  };

  // Notes about name changes in certain sections
  var addInstitutionalTabNote = function() {
    var descriptionText = {
      'main_es':  '<p>El apartado ¿Quién lo gasta? muestra la información de los órganos gestores del gasto atendiendo ' +
                  'a la estructura vigente en el momento de la consulta, si nos encontramos en un ejercicio en curso, o la vigente ' +
                  'al final de año, si se trata de ejercicios finalizados. En los años que se produzcan cambios en la organización ' +
                  'administrativa del Ayuntamiento que supongan la supresión de órganos gestores del gasto, se muestran los importes ' +
                  'presupuestados y gastados por dichos órganos hasta su desaparición.',
      'main_en':  '<p>The section "Who spent it?" displays information about the spending managing bodies according to the ' +
                  'current structure at the time of the query, if it is in an ongoing fiscal year, or the structure in place ' +
                  'at the end of the year if it pertains to completed fiscal years. In years when there are changes in the ' +
                  'administrative organization of the City Council resulting in the elimination of spending bodies, ' +
                  'the amounts budgeted and spent  by those bodies until their disappearance are shown.'
    };

    var descriptions = {
      '/es/politicas': descriptionText['main_es'],
      '/en/politicas': descriptionText['main_en'],
    };

    var description = descriptions[ window.location.pathname ];

    if (description) {
      $('.policies .policies-content .policies-chart').append( '<div class="hidden custom-note institutional-note policy-description">'+description+'</div>' );
    }
  };

  var addInstitutionalDescriptions = function() {
    var descriptionText = {
      '120_es':   '<p>En agosto de 2023, se unieron las secciones de "Portavoz, Seguridad y Emergencias", "Coordinación Territorial, ' +
                  'Transparencia y Participación Ciudadana", "Internacionalización y Cooperación" y "Vicealcaldía", ' +
                  'pasando a denominarse la nueva sección "Vicealcaldía, Portavoz, Seguridad y Emergencias". Es por ello que la serie ' +
                  'temporal de datos se rompe en 2023: comparar secciones con competencias distintas sería engañoso.',
      '140_es':   '<p>En agosto de 2023, se unieron las secciones de "Economía, Innovación y Empleo" y "Hacienda y Personal", ' +
                  'pasando a denominarse la nueva sección "Economía, Innovación y Hacienda". Es por ello que la serie ' +
                  'temporal de datos se rompe en 2023: comparar secciones con competencias distintas sería engañoso.',
      '150_es':   '<p>En agosto de 2023, se unieron las secciones de "Desarrollo Urbano" y "Medio Ambiente y Mobilidad", ' +
                  'pasando a denominarse la nueva sección "Urbanismo, Medio Ambiente y Mobilidad". Es por ello que la serie ' +
                  'temporal de datos se rompe en 2023: comparar secciones con competencias distintas sería engañoso.',

      '120_en':   '<p>In August 2023, the sections "Spokesperson, Public Safety, and Emergencies," "Territorial Coordination, Transparency ' +
                  'and Citizen Participation," "Internationalization and Cooperation," and "Deputy Mayor\'s Office" were merged, and ' +
                  'they are now referred to as the new section "Deputy Mayor\'s Office, Spokesperson, Public Safety, and Emergencies." ' +
                  'This is why the data time series is interrupted in 2023: comparing sections with different competences would be ' +
                  'misleading.',
      '140_en':   '<p>In August 2023, the sections "Economy, Innovation, and Employment" and "Treasury and Personnel" were merged, ' +
                  'and they are now referred to as the new section "Economy, Innovation, and Treasury." This is why the data time ' +
                  'series is interrupted in 2023: comparing sections with different competences would be misleading.',
      '150_en':   '<p>In August 2023, the sections "Urban Development" and "Environment and Mobility" were merged, and they are now ' +
                  'referred to as the new section "Urban Planning, Environment, and Mobility." This is why the data time series is ' +
                  'interrupted in 2023: comparing sections with different competences would be misleading.',
    };

    var descriptions = {
      '/es/secciones/012A': descriptionText['120_es'],
      '/es/secciones/0120': descriptionText['120_es'],
      '/es/secciones/014A': descriptionText['140_es'],
      '/es/secciones/0140': descriptionText['140_es'],
      '/es/secciones/015A': descriptionText['150_es'],
      '/es/secciones/0150': descriptionText['150_es'],

      '/en/secciones/012A': descriptionText['120_en'],
      '/en/secciones/0120': descriptionText['120_en'],
      '/en/secciones/014A': descriptionText['140_en'],
      '/en/secciones/0140': descriptionText['140_en'],
      '/en/secciones/015A': descriptionText['150_en'],
      '/en/secciones/0150': descriptionText['150_en'],
    };

    var description = descriptions[ window.location.pathname.substring(0,window.location.pathname.lastIndexOf('/')) ];

    if (description) {
      $('.policies .policies-content .policies-chart').append( '<div class="custom-note institutional-note policy-description">'+description+'</div>' );
    }
  };

  // Custom description for investments
  var addInvestmentsDescriptions = function() {
    var lang = $('html').attr('lang')

    var description = {
      'es': '<p>(*) La clasificación de las inversiones del Ayuntamiento y de los Organismos Autónomos se '+
            'realiza siguiendo la estructura que establece la Orden EHA/3565/2008 de 3 de diciembre, por la que se aprueba '+
            'la estructura de los presupuestos de las entidades locales.</p><p>En el Ayuntamiento de Madrid, además, se '+
            'utiliza una clasificación por líneas de inversión, herramienta más sencilla y simplificada para analizar y '+
            'exponer el destino de las inversiones.</p>',
      'en': '<p>(*) The classification of the investments of the City Council and the Autonomous Bodies is made following ' +
            'the structure established by Order EHA/3565/2008 of December 3, which approves the structure for the budgets of ' +
            'local entities.</p><p>In Madrid City Council, a classification by investment lines is also used, a simpler tool ' +
            'to analyze and expose the destination of investments.</p>'
    }

    var investmentLineIntro = {
      'es': '<p>Líneas de inversión en el distrito <a href="#policy-description-box">(*)</a></p>',
      'en': '<p>Investment lines in the district <a href="#policy-description-box">(*)</a></p>'
    }

    if ($('section.investment-breakdown').length) {
      $('#policy-chart-container').before('<div class="investment-line-intro">'+investmentLineIntro[lang]+'</div>');
      $('.investments .investments-content .panel-downloads').before('<div id="policy-description-box" ' +
        'class="policy-description">'+description[lang]+'</div>');
    }

    var ifsNote = {
      'es': '<p style="font-weight: 400 !important;">' +
            'Del total de dinero presupuestado en inversiones, un porcentaje elevado son inversiones financieramente ' +
            'sostenibles (IFS) que, tal como establece la normativa vigente, se pueden ejecutar en dos ejercicios presupuestarios. En ' +
            'consecuencia para evaluar la ejecución de estos proyectos habrá que esperar a que transcurra el ejercicio posterior. ' +
            'Dichas inversiones se distinguen mediante un identificador que aparece al principio del texto descriptivo de los mismos: IFS.</p>' +
            '<p style="font-weight: 400 !important;">' +
            'Las IFS se habilitan en el presupuesto mediante créditos extraordinarios y suplementos de crédito que exigen los mismos ' +
            'trámites que la aprobación del presupuesto general, por lo que el período de tramitación es largo y, como consecuencia, la ' +
            'ejecución del gasto en el primer ejercicio es menor.</p>',
      'en': '<p style="font-weight: 400 !important;">' +
            'Of the total money budgeted in investments, a high percentage are financially sustainable investments (IFS) that, as ' +
            'established by current regulations, can be executed in two budgetary years. Consequently, in order to evaluate the execution ' +
            'of these projects, it will be necessary to wait until the following year. These investments are distinguished by an identifier ' +
            'that appears at the beginning of the descriptive text of the same: IFS.</p>' +
            '<p style="font-weight: 400 !important;">' +
            'IFSs are enabled in the budget through extraordinary ' +
            'loans and credit supplements that require the same procedures as the approval of the general budget, so the processing period is ' +
            'long and, as a consequence, the execution of the expenditure in the first year is lower.</p>'
    }

    // We want to show the message only when IFS are applicable. Since we don't have the year handy at this point,
    // we use the `total-special` class to show/hide the message. But this forces us to counteract the styling from
    // the class. Not the most elegant solution, but it works.
    if ($('.investments-content #main-total').length) {
      $('.investments-content #main-total').after('<div class="policy-description total-special" style="border-top: none">'+ifsNote[lang]+'</div>');
    }
  };

  var addMainInvestmentsYearSelectorCustomTitle = function () {
    var title = {
      'es': 'Elige el rango de años',
      'en': 'Select the year range',
    };
    $('.main-investments .layout-slider p.title').text(title[$('html').attr('lang')]);
  };

  var addMainInvestmentsFootnote = function () {
    var footnote = {
      'es': 'Las inversiones completadas aparecen marcadas con el icono ✔️.',
      'en': 'Completed investments are marked with the ✔️ icon.',
    };
    $('.main-investments .panel-downloads').before("<p style='text-align: center; font-weight: 300;'>"+footnote[$('html').attr('lang')]+"</p>");
  };

  // Swap order of budgeted/actual totals in Overview page
  var swapTotalsInOverview = function() {
    $(".total-budgeted").prependTo(".budget-totals .panel-content");
  };

  var addIEAdvice = function() {
    var ua = window.navigator.userAgent;
    if ($('body').hasClass('body-payments')) {
      console.log(ua)
      if (ua.indexOf('MSIE') > 0 || ua.indexOf('Trident/') > 0) {
        $('.payments-content > .container').first().prepend('<p class="alert alert-danger" style="margin-top: 30px; font-size: 1.5rem;">Su navegador puede presentar problemas de rendimiento en esta sección. Le recomendamos utilizar <a href="https://www.google.es/chrome/" title="Google Chrome" target="_blank" rel="nofollow">Google Chrome</a> o <a href="https://www.mozilla.org/es-ES/firefox/new/" title="Mozilla Firefox" target="_blank" rel="nofollow">Mozilla Firefox</a> para un mejor rendimiento.</p>');
      }
    }
  }

  addYearSelectorCustomLabels();

  // Setup lang dropdown
  $('.dropdown-toggle').dropdown();

  addChartsAlert('.policies-content .policies-chart');
  addChartsAlert('.sankey-container');
  addChartsAlert('.payments-content');
  addChartsAlert('.investments-content');
  addChartsAlert('.main-investments-content');
  addChartsAlert('.monitoring-content');

  swapTotalsInOverview();

  addCustomDescriptions();
  addInstitutionalTabNote();
  addInstitutionalDescriptions();
  addInvestmentsDescriptions();

  addMainInvestmentsYearSelectorCustomTitle();
  addMainInvestmentsFootnote();

  addIEAdvice();
});
