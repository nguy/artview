


.. raw:: html


    <style type="text/css">

    .figure {
        float: left;
        margin: 10px;
        -webkit-border-radius: 10px; /* Saf3-4, iOS 1-3.2, Android <1.6 */
        -moz-border-radius: 10px; /* FF1-3.6 */
        border-radius: 10px; /* Opera 10.5, IE9, Saf5, Chrome, FF4, iOS 4, Android 2.1+ */
        border: 2px solid #fff;
        background-color: white;
        /* --> Thumbnail image size */
        width: 150px;
        height: 100px;
        -webkit-background-size: 150px 100px; /* Saf3-4 */
        -moz-background-size: 150px 100px; /* FF3.6 */
    }

    .figure img {
        display: inline;
    }

    div.docstringWrapper p.caption {
        display: block;
        -webkit-box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.0);
        -moz-box-shadow: 0px 0px 20px rgba(0, 0, 0, .0); /* FF3.5 - 3.6 */
        box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.0); /* Opera 10.5, IE9, FF4+, Chrome 10+ */
        padding: 0px;
        border: white;
    }

    div.docstringWrapper p {
        display: none;
        background-color: white;
        -webkit-box-shadow: 0px 0px 20px rgba(0, 0, 0, 1.00);
        -moz-box-shadow: 0px 0px 20px rgba(0, 0, 0, 1.00); /* FF3.5 - 3.6 */
        box-shadow: 0px 0px 20px rgba(0, 0, 0, 1.00); /* Opera 10.5, IE9, FF4+, Chrome 10+ */
        padding: 13px;
        margin-top: 0px;
        border-style: solid;
        border-width: 1px;
    }


    </style>


.. raw:: html


        <script type="text/javascript">

        function animateClone(e){
          var position;
          position = $(this).position();
          var clone = $(this).closest('.thumbnailContainer').find('.clonedItem');
          var clone_fig = clone.find('.figure');
          clone.css("left", position.left - 70).css("top", position.top - 70).css("position", "absolute").css("z-index", 1000).css("background-color", "white");

          var cloneImg = clone_fig.find('img');

          clone.show();
          clone.animate({
                height: "270px",
                width: "320px"
            }, 0
          );
          cloneImg.css({
                'max-height': "200px",
                'max-width': "280px"
          });
          cloneImg.animate({
                height: "200px",
                width: "280px"
            }, 0
           );
          clone_fig.css({
               'margin-top': '20px',
          });
          clone_fig.show();
          clone.find('p').css("display", "block");
          clone_fig.css({
               height: "240",
               width: "305px"
          });
          cloneP_height = clone.find('p.caption').height();
          clone_fig.animate({
               height: (200 + cloneP_height)
           }, 0
          );

          clone.bind("mouseleave", function(e){
              clone.animate({
                  height: "100px",
                  width: "150px"
              }, 10, function(){$(this).hide();});
              clone_fig.animate({
                  height: "100px",
                  width: "150px"
              }, 10, function(){$(this).hide();});
          });
        } //end animateClone()


        $(window).load(function () {
            $(".figure").css("z-index", 1);

            $(".docstringWrapper").each(function(i, obj){
                var clone;
                var $obj = $(obj);
                clone = $obj.clone();
                clone.addClass("clonedItem");
                clone.appendTo($obj.closest(".thumbnailContainer"));
                clone.hide();
                $obj.bind("mouseenter", animateClone);
            }); // end each
        }); // end

        </script>



Examples
========

.. _examples-index:
