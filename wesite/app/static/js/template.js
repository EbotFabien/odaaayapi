var count=0;
var page =1;
let seq = 1;
(function($) {

    "use strict";

    Dropzone.autoDiscover = false;

    $(document).ready(function() {

        //
        // Horizontal scroll
        //
        let url = $(location).attr('href');
        let id = url.split("/")[4];
        if(id){
          summary(id);
        }else{

        }

        [].forEach.call(document.querySelectorAll('[data-horizontal-scroll]'), function (el) {
            function scrollHorizontally(e) {
                e = window.event || e;
                var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
                el.scrollLeft -= (delta*28);
                e.preventDefault();
            }

            if (el.addEventListener) {
                el.addEventListener("mousewheel", scrollHorizontally, false);
                el.addEventListener("DOMMouseScroll", scrollHorizontally, false);
            } else {
                el.attachEvent("onmousewheel", scrollHorizontally);
            }
        });

        //
        // Detect mobile devices
        //

        var isMobile = {
            Android: function() {
                return navigator.userAgent.match(/Android/i);
            },
            BlackBerry: function() {
                return navigator.userAgent.match(/BlackBerry/i);
            },
            iOS: function() {
                return navigator.userAgent.match(/iPhone|iPod|iPad/i);
            },
            Opera: function() {
                return navigator.userAgent.match(/Opera Mini/i);
            },
            Windows: function() {
                return navigator.userAgent.match(/IEMobile/i) || navigator.userAgent.match(/WPDesktop/i);
            },
            any: function() {
                return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
            }
        };

        //
        // Modified accordion(settings.html)
        //

        if ( !isMobile.any() ) {
            [].forEach.call(document.querySelectorAll('.modified-accordion [data-toggle="collapse"]'), function (e) {
                e.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                });
            });

            [].forEach.call(document.querySelectorAll('.modified-accordion .collapse'), function (e) {
                e.classList.add('show');
            });
        }

        //
        // Emoji
        //

        if ( !isMobile.any() ) {
            [].forEach.call(document.querySelectorAll('[data-emoji-form]'), function (form) {
                var button = form.querySelector('[data-emoji-btn]');

                var picker = new EmojiButton({
                    position: "top",
                    zIndex: 1020
                });

                picker.on('emoji', function(emoji) {
                    form.querySelector('[data-emoji-input]').value += emoji;
                });

                button.addEventListener('click', function () {
                    picker.pickerVisible ? picker.hidePicker() : picker.showPicker(button);
                });
            });
        } else {
            [].forEach.call(document.querySelectorAll('[data-emoji-form]'), function (form) {
                form.querySelector('[data-emoji-btn]').style.display = 'none';
            });
        }

        //
        // Toggle chat
        //

        [].forEach.call(document.querySelectorAll('[data-chat="open"]'), function (a) {
            a.addEventListener('click', function () {
                document.querySelector('.main').classList.toggle('main-visible');
            }, false );
        });

        //
        // Toggle chat`s sidebar
        //

        [].forEach.call(document.querySelectorAll('[data-chat-sidebar-toggle]'), function (e) {
            e.addEventListener('click', function (event) {
                event.preventDefault();
                var chat_sidebar_id = e.getAttribute('data-chat-sidebar-toggle');
                var chat_sidebar = document.querySelector(chat_sidebar_id);

                if (typeof(chat_sidebar) != 'undefined' && chat_sidebar != null) {
                    if ( chat_sidebar.classList.contains('chat-sidebar-visible') ) {
                        chat_sidebar.classList.remove('chat-sidebar-visible')
                        document.body.classList.remove('sidebar-is-open');
                    } else {
                        [].forEach.call(document.querySelectorAll('.chat-sidebar'), function (e) {
                            e.classList.remove('chat-sidebar-visible');
                            document.body.classList.remove('sidebar-is-open');
                        });
                        chat_sidebar.classList.add('chat-sidebar-visible');
                        document.body.classList.add('sidebar-is-open');
                    }
                }

            });
        });

        //
        // Close all chat`s sidebars
        //

        [].forEach.call(document.querySelectorAll('[data-chat-sidebar-close]'), function (a) {
            a.addEventListener('click', function (event) {
                event.preventDefault();
                document.body.classList.remove('sidebar-is-open');
                [].forEach.call(document.querySelectorAll('.chat-sidebar'), function (a) {
                    a.classList.remove('chat-sidebar-visible');
                });
            }, false );
        });

        //
        // Dropzone
        //

        if ( document.querySelector('#dropzone-template-js') ) {
            var template = document.querySelector('#dropzone-template-js');
            var template_element = document.querySelector('#dropzone-template-js');
            template_element.parentNode.removeChild(template_element);
        }

        [].forEach.call(document.querySelectorAll('.dropzone-form-js'), function (el) {

            var clickable         = el.querySelector('.dropzone-button-js').id;
            var url               = el.getAttribute('data-dz-url');
            var previewsContainer = el.querySelector('.dropzone-previews-js');

            var myDropzone = new Dropzone(el, {
                url: url,
                previewTemplate: template.innerHTML,
                previewsContainer: previewsContainer,
                clickable: '#' + clickable
            });
        });

        //
        // Mobile screen height minus toolbar height
        //

        function mobileScreenHeight() {
            if ( document.querySelectorAll('.navigation').length && document.querySelectorAll('.sidebar').length ) {
                document.querySelector('.sidebar').style.height = windowHeight - document.querySelector('.navigation').offsetHeight + 'px';
            }
        }

        if ( isMobile.any() && (document.documentElement.clientWidth < 1024) ) {
            var windowHeight = document.documentElement.clientHeight;
            mobileScreenHeight();

            window.addEventListener('resize', function(event){
                if (document.documentElement.clientHeight != windowHeight) {
                    windowHeight = document.documentElement.clientHeight;
                    mobileScreenHeight();
                }
            });
        }

        //
        // Scroll to end of chat
        //

        if (document.querySelector('.end-of-chat')) {
            document.querySelector('.end-of-chat').scrollIntoView();
        }

        //
        // Autosize
        //

        autosize(document.querySelectorAll('[data-autosize="true"]'));

        //
        // SVG inject
        //

        SVGInjector(document.querySelectorAll('img[data-inject-svg]'));

    });

})(jQuery);
var btn = $('#back-to-top');
var btn2= $("#top-minor");
$("#more").hide();
$('#first_scroll').onscroll = function() {scrollFunction()};

function scrollFunction() {
    if ($('#first_scroll').scrollTop > 20) {
        btn.show();
        console.log('s');
    } else {
        btn.hide();
        console.log('h');
    }
}
btn.on('click', function(e) {
  e.preventDefault();
  $('html,#first_scroll').animate({scrollTop:0}, '300');     
});
if(count == 0){
  $("#nbadge").hide();
}
$("#search").keyup(function(){
  let word = $(this).val();
  search(word);
});
function summary(id){
  $('.loading-image').show();
  $.ajax({
    url: "/summary/"+id+"?json=1",
    type: 'GET',
    dataType: 'json',
    success: function(res) {
      $('#awsome-content').html("<h5>Summary</h5><br>"+res['content']);
      $('#title').html(res['title']);
      $('#content').html(res['data']);
      $('#source').html(res['source']);
      $('#source_desc').html(res['description']);
      window.history.pushState("", "", "/summary/"+id);
      $('#more-btn').attr('href',res['link']);
      $('#source_desc').html(res['description']);
      $('#feed').addClass( "main-visible" );
      $('#slogo').attr('src', '/static/images/'+res['source']+'.svg');
      $("#more").show();
    },
    complete: function(){
      $('.loading-image').hide();
    }
  });
}

function search(word){
  $.ajax({
    url: "/search?keyword="+word,
    type: 'GET',
    success: function(res){
      if(res['res'] === 'none'){

      } else {
        results = JSON.parse(res)
        $('#sidepost').empty();
        results.forEach(element => order(element));
      }
    }
  });
}

$('#toggle').click(function (){
  var theme = $('#theme').attr('href');
  if(theme == '/static/css/template.min.css'){
    $('#theme').attr('href','/static/css/template.dark.min.css');
  }
  if(theme == '/static/css/template.dark.min.css'){
    $('#theme').attr('href','/static/css/template.min.css');
  }
  seq++;
});

function order(element){
  if(element['thumb']){
    template = `
      <a id="`+element['id']+`" class="text-reset nav-link p-0 mb-6" href="#" onclick="summary(`+element['id']+`)">
        <div class="card mb-3">
            <img src="`+element['thumb']+`" class="card-img-top card-img" alt="`+element['title']+`">
            <div class="card-body">
                <h5 class="card-title">`+element['title']+`</h5>
                <p class="card-text"><small class="text-muted">`+element['pubdate']+`</small></p>
            </div>
        </div>
      </a>
    `;
    $('#sidepost').append(template);  
  }else{
    template = `
      <a id="`+element['id']+`" class="text-reset nav-link p-0 mb-6" href="#" onclick="summary(`+element['id']+`)">
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">`+element['title']+`</h5>
                <p class="card-text"><small class="text-muted">`+element['pubdate']+`</small></p>
            </div>
        </div>
      </a>
    `;
    $('#sidepost').append(template);
  }
}
$( document ).ready(function() {
  var sharect = new Sharect();
  sharect.config({
    facebook: true,
    twitter: true,
    selectableElements: ['body']
  }).init();
  new needShareDropdown(document.getElementById('share-button'), {
    iconStyle: 'box',
    boxForm: 'vertical',
    networks: 'Mailto,Twitter,Facebook',
    boxForm: 'horizontal',
    position: 'topCenter'
  });
  $("#back").click(function(){
    $('#feed').removeClass( "main-visible" );
  });
  $('[data-toggle="popover"]').popover();
  setInterval(notify,60000);
  if ($('#back-to-top').length) {
    var scrollTrigger = 100, // px
    backToTop = function () {
      var scrollTop = $(window).scrollTop();
      if (scrollTop > scrollTrigger) {
        $('#back-to-top').addClass('show');
      } else {
        $('#back-to-top').removeClass('show');
      }
    };
    backToTop();
    $(window).on('scroll', function () {
      backToTop();
    });
    $('#back-to-top').on('click', function (e) {
      e.preventDefault();
      $('html,body').animate({
          scrollTop: 0
      }, 700);
      $('#scroll').animate({
          scrollTop: 0
      }, 700);
    });
  }
});
function notify(){
  $.ajax({
    url: "/notification",
    type: 'GET',
    success: function(res){
      if(res['res'] === 'none'){
          console.log("result is none");
      } else {
        results = JSON.parse(res);
        results.forEach(element => add_not(element));
      }
    }
  });
  
}
function add_not(element,index){
  var A=localStorage.getItem(element['uuid']);
  if(A){
    
  }
  else{
    $("#nbadge").show();
    count++;
    localStorage.setItem(element['uuid'],index);
    $("#noti").text(count);
  } 

}
function newcart(page){
  $.ajax({
    url: "/new?page="+page+'&count=10',
    type: 'GET',
    success: function(res){
      if(res['res'] === 'none'){

      } else {
        $("#loading").hide();
        results = JSON.parse(res)
        results.forEach(element => order(element));
      }
    }
  });
}
$("#first_scroll").scroll(function(){
  var ele = document.getElementById('first_scroll');

  if((ele.scrollHeight - ele.scrollTop) <= ele.clientHeight){
    newcart(page);
    page++;
  }
  $("#loading").show();
});