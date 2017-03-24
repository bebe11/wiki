$(function() {
    
	$("#getTableButton").hide();
    $("#exportButton").hide();
	$("#viz_type_div").hide();
    $("#xInput").hide();
	$("#yInput").hide();
    $("#axis").hide();
    $("#resetButton").hide();
    $("#analysisButton").hide();
    $("#title").hide();
    $("#xTitle").hide();
    $("#yTitle").hide();
    $("#aggregate").hide();
    
    countX = 0;
    countY = 0;
    
    submit();
    getTable();
    analysis();
    
    $('#resetButton').click(function(){
         $("#table table tr td, #table table tr th").each(function(){
            $(this).css("border", "1px solid #ddd");
        });
        $("input[name=axisName]:checked").each(function(){
            this.checked = false;  
        });
        $("#xInput").html('');
        $("#yInput").html('');
        countX = 0;
        countY = 0;
    });

    $('#nextButton').click(function(){
        var right = parseInt($('.image-holder').css("right"));
        console.log(right);
        $('.image-holder').css('right', right + 1000);
    });

     $('#previousButton').click(function(){
        var left = parseInt($('.image-holder').css("left"));
        console.log(left);
        $('.image-holder').css('left', left - 1000);
    });

    
    $('#table').hover(function() {
        var axisVal = $("input[name=axisName]:checked").val();
        var tds = $("th");
        var changeColumnColor = function() {
            var el = this;
            ownerIndex = $('th:contains("' + el.innerHTML + '")').index();
            if (axisVal == 'x' && countX < 1) {
                if ($("#yInput").text() != el.innerHTML){

                    $('#table table tr td:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid red");
                    $('#table table tr th:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid red");
                    $("#xInput").html(el.innerHTML);
                    countX++;
                }
            }
            if (axisVal == 'y' && countY < 1) {
                if ($("#xInput").text() != el.innerHTML){
                    $('#table table tr td:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid black");
                    $('#table table tr th:nth-child('+ (ownerIndex + 1) +')').css("border", "3px solid black");
                    $("#yInput").html(el.innerHTML);
                    countY++;
                }
            }
        };

        for(var i = 0; i < tds.length; i++) {
          tds[i].onclick = changeColumnColor;
        };
    });  
});

function submit(){
    $('#button').click(function(){
        var url = $('#txtUrl').val();
        $.ajax({
            url: '/getWikiTables',
            data: {'url': url},
            // cache: false,
            type: 'POST',
            success: function(response){
                $("#getTableButton").show();
                $("#exportButton").show();
                $('#tables').append(response);
            },
            error: function(error){
                console.log(error);
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
            $('#tables div').css("border", "0px solid black");
            $('#' + el.id).parent().css("border", "3px solid black");
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
                $('#table').append(response);
				$("#viz_type_div").show();
                $("#xInput").show();
                $("#yInput").show();
                $("#axis").show();
                $("#resetButton").show();
                $("#analysisButton").show();
                $("#title").show();
                $("#xTitle").show();
                $("#yTitle").show();
                $("#aggregate").show();
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
        $.ajax({
            url: '/vizType',
            data: {'viz': viz, 'x': x, 'y': y, 'aggregate': aggregate, 'title': title, 'xTitle': xTitle, 'yTitle': yTitle},
            type: 'POST',
            success: function(response){
                $('#table').replaceWith(response);
            },
            error: function(error){
                console.log(error);
            }
        });
    });
}
