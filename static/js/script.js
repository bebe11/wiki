$(function() {
    $("#txtUrl").bind('keypress', function(e) {
    var code = e.which;
    console.log(code);
});
	$("#panel1").hide();
    $("#panel2").hide();
    
    countX = 0;
    countY = 0;
    var checked = ''
    
    submit();
    getTable();
    analysis();
    reset();

    $('#xInput').click(function(){
         $("#yInput").removeAttr("style");
         $('#xInput').css("border", "3px solid #905f98")
         checked = 'x'
    });

    $('#yInput').click(function(){
         $("#xInput").removeAttr("style");
         $('#yInput').css("border", "3px solid #905f98")
         checked = 'y'
    });

    $('#table').hover(function() {
        var ths = $("th");

        var changeColumnColor = function() {
            var el = this;
            ownerIndex = $('th:contains("' + el.innerHTML + '")').index();
            if (checked == 'x' && countX < 1) {
                if ($("#yInput").text() != el.innerHTML){
                    $('#table tr td:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid #905f98");
                    $('#table tr th:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid #905f98");
                    $("#xInput").html(el.innerHTML);
                    countX++;
                }
            }
            if (checked == 'y' && countY < 1) {
                if ($("#xInput").text() != el.innerHTML){
                    $('#table tr td:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid #905f98");
                    $('#table tr th:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid #905f98");
                    $("#yInput").html(el.innerHTML);
                    countY++;
                }
            }
        };

        for(var i = 0; i < ths.length; i++) {
          ths[i].onclick = changeColumnColor;
        };

    });

     $('#resetButton').click(function(){
        reset();
     });
});

function reset(){
    $("#table tr td, #table table tr th").each(function(){
        $(this).css("border", "1px solid #ddd");
    });
    $('#table').show();
    $('#img').empty();
    $("#xInput").html('');
    $("#yInput").html('');
    countX = 0;
    countY = 0;
}

function submit(){
    $('#button').on('click', function () {
        var $btn = $(this).button('loading')
        var url = $('#txtUrl').val();
        $.ajax({
            url: '/getWikiTables',
            data: {'url': url},
            type: 'POST',
            success: function(response){
                $('#tables').empty();
                $("#panel1").show();
                $('#tables').append(response);
                $btn.button('reset');
            },
            error: function(error){
                console.log(error);
                $btn.button('reset');
            }
        });
    });
}

function getTable(){
    var selectedTable = '';

    $('#tables').bind("DOMSubtreeModified",function(){
        var table = $("table");

        var getParentTableID = function() {
            var el = this;
            $("table").removeAttr("style");
            $('#' + el.id).css("border", "4px solid #000");
            selectedTable = el.id;
        };

        for(var i = 0; i < table.length; i++) {
          table[i].onclick = getParentTableID;
        };
    });
    $('#getTableButton').click(function() {
        $.ajax({
            url: '/getTable',
            data: {table_id: selectedTable}, //$('form').serialize(),
            // cache: false,
            type: 'POST',
            success: function(response){
                   reset();
                   $('#table').empty();
                   $('#img').empty();
                   $('#table').append(response);
                   $("#panel2").show();
            },
            error: function(error){
                console.log(error);
            }
        });
    });  
    
}

function analysis(){
    $('#analysisButton').click(function() {
        var viz = $('#viz_type_div').val();
        var aggregate = $('#aggregate').val();
        var title = $('#title').val();
        var xTitle = $('#xTitle').val();
        var yTitle = $('#yTitle').val();
        var x = $('th:contains("' + $("#xInput").text() + '")').index();
        var y = $('th:contains("' + $("#yInput").text() + '")').index();
        var sort = $("input[name=sortRadios]:checked").val();
        $.ajax({
            url: '/vizType',
            data: {'viz': viz, 'x': x, 'y': y, 'aggregate': aggregate, 'title': title, 'xTitle': xTitle, 'yTitle': yTitle, 'sort': sort},
            type: 'POST',
            success: function(response){
                $('#img').empty();
                $('#table').hide();
                //$('#table').replaceWith(response);
                $('#img').append(response);
            },
            error: function(error){
                console.log(error);
            }
        });
    });
}
