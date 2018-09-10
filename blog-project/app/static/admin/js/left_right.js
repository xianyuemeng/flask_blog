$('#left_btn').click(function(){
    var num = {{ request.args.get('p',1) }}
    $(".pagination ul li").eq(num-1).find('.cli').append("<span></span>")
    $(".pagination ul li").eq(num-1).find('.cli span').click()
    })

$('#right_btn').click(function(){
    var num = {{ request.args.get('p',1) }}
    $(".pagination ul li").eq(num+1).find('.cli').append("<span></span>")
    $(".pagination ul li").eq(num+1).find('.cli span').click()
})