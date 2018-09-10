$("input[type='file']").change(function(){
    var file = this.files[0];
    if (window.FileReader) {
         var reader = new FileReader();
         reader.readAsDataURL(file);
         //监听文件读取结束后事件
         reader.onloadend = function (e) {
             $(".ppic").attr("src", e.target.result);    //e.target.result就是最后的路径地址
         };
    }
});