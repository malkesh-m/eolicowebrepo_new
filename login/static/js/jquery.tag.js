/**
 * jquery.tag.js
 * @license	GPL
 * @author	zhujie
 * @site	http://www.cnzhujie.cn
 * */
;(function($)
{	
	/**
	 * 初始化标签配置
	 */
	$.fn.tagsOpReset=function(){
		$(this).data('input',true);
		$(this).data('inputNote',"");
		$(this).data('beforeInput',null);
		$(this).data('afterInput',null);
		$(this).data('del',true);
		$(this).data('onDel',null);
		$(this).data('repeat',true);
		$(this).data('onRepeat',null);
		$(this).data('max',0);
		$(this).data('action',false);
		$(this).data('count',0);
		$(this).data('theme','blue');
	},
	/**
	 * 配置标签设置（option为配置对象，其可配置属性如下）
	 *	@param input	boolean	是否创建标签input（在input上回车生成标签）(默认true)
	 *	@param inputNote	string	显示在input上面的提示（例如‘输入后请回车’）
	 *	@param beforeInput	function	input中回车添加标签之前的函数（默认null）
	 *	@param afterInput	function	input中回车添加标签之后的函数（默认null）
	 *	@param del	boolean	是否可以删除标签(默认true)
 	 *	@param onDel	function	删除标签之前的函数（默认null）
 	 *  @param repeat	boolean OR String	添加标签时候是否检测重复(默认true),false表示不检查，不为空字符串表示检查并弹出对话框提示
	 *  @param onRepeat	function	添加标签时候检测到重复标签时执行的函数(默认null)
	 *	@param max	number	最多标签数目(小于等于0不限制)（默认不限制）
 	 *	@param action	boolean OR object OR function	每个标签的点击动作（false：点击没反映。object{href:链接(%v%表示tagValue,%id%表示tagId),target:...}：打开链接。function：点击时执行此函数，函数参数为tagValue,tagId
	 *	@param theme string	css主题（默认blue）
	 * */
	$.fn.tagsOpSet=function(option){
		if(typeof(option)!='object')return;
		if(typeof(option.repeat)=='boolean' || typeof(option.repeat)=='string'){
			$(this).data('repeat',option.repeat);
		}
		if(typeof(option.del)=='boolean'){
			$(this).data('del',option.del);
		}
		if(typeof(option.input)=='boolean'){
			$(this).data('input',option.input);
		}
		if(typeof(option.inputNote)=='string'){
			$(this).data('inputNote',option.inputNote);
		}
		if(typeof(option.beforeInput)=='function'){
			$(this).data('beforeInput',option.beforeInput);
		}
		if(typeof(option.afterInput)=='function'){
			$(this).data('afterInput',option.afterInput);
		}
		if(typeof(option.onDel)=='function'){
			$(this).data('onDel',option.onDel);
		}
		if(typeof(option.max)=='number'){
			$(this).data('max',option.max);
		}
		if(typeof(option.action)=='boolean' || typeof(option.action)=='function' || 
			typeof(option.action)=='object'){
			$(this).data('action',option.action);
		}
		if(typeof(option.link)=='string'){
			$(this).data('link',option.link);
		}
		if(typeof(option.theme)=='string'){
			$(this).data('theme',option.theme);
		}
	},
	/**
	 * 创建初始化标签
	 * @param option object 配置对象
	 */
	$.fn.tagsInit=function(option){
		var $tagdiv=$(this);
		//初始化配置
		$tagdiv.tagsOpReset();
		$tagdiv.tagsOpSet(option);
		//创建标签容器
		var tagper=$tagdiv.attr("tagname");
		if(typeof(tagper)=="undefined" || tagper==""){
			tagper=new Date().getTime();
			$tagdiv.attr("tagname",tagper);
		}
		
		//创建容器
		var oDiv=$("<div class='"+$tagdiv.data('theme')+" tag-contain tag-clearfix'></div>").insertAfter(this); 
		//创建ul
		var oUl=$("<ul id='"+tagper+"_tag_list'></ul>").insertAfter(oDiv);
		$('<div style="clear:both;height:0px;"></div>').insertAfter(oDiv);//清理浮动
		//标签input
		if($tagdiv.data('input')){
			var note=$tagdiv.data('inputNote');
			//创建input
			var oInput=$("<input type='text' value='"+note+"' title='"+note+"' placeholder='Select or Search Agent' class='tag-input tag-input-blur' id='"+tagper+"_tag_input' />").appendTo(oDiv);
			//给input添加事件
			oInput.keydown(function(e){
				if(e.keyCode==13){
					if(this.value!=""){
						//添加之前执行的函数
						try{
							var beforeInput=$tagdiv.data('beforeInput');
							if(typeof(beforeInput)=='function'){//返回值为false时，停止添加
								if(beforeInput(this.value)==false)return;
							}
						}catch(e){return;}
						//添加
						if(!$tagdiv.tagsAdd(this.value))return;
						//添加之后执行的函数
						try{
							var afterInput=$tagdiv.data('afterInput');
							if(typeof(afterInput)=='function'){
								afterInput(this.value);
							}
						}catch(e){}
						this.value='';
					}					
				}
			});
			oInput.focus(function(){
				if(this.value==note)this.value="";
				$(this).removeClass("tag-input-blur");
			});
			oInput.blur(function(){
				if(this.value=='')this.value=note;
				$(this).addClass("tag-input-blur");
			});
			return $tagdiv;
		}
	},
	/**
	*添加标签（tagValue是必不可少的）
	*tagValue----标签内容
	*tagId-------标签id
	*/
	$.fn.tagsAdd=function(tagValue,tagId){
		var $tagdiv=$(this);
		//标签前缀
		var tagper=$tagdiv.attr("tagname");
		if(typeof(tagper)=="undefined" || tagper=="")return false;
		//判断标签个数是否超过限制
		var count=$(this).data('count');
		var max=$(this).data('max');
		if(max>0 && count>=max)return false;
		//检查参数
		if(!tagValue)return false;
		if(typeof(tagId)=='undefined')tagId=0;
		//检测是否重复
		var repeat=$tagdiv.data('repeat');
		if(repeat!=false && $tagdiv.tagsIndexof(tagValue,tagId)!=-1){
			if(typeof(repeat)=='string' && repeat!=''){
				alert(repeat);
			}
			try{
				var onRepeat=$tagdiv.data('onRepeat');
				if(typeof(onRepeat)=='function'){
					onRepeat(tagValue,tagId);
				}
			}catch(e){}
			return false;
		}
		//添加标签
		var ul=$("#"+tagper+"_tag_list");
		var li=$("<li title='"+tagValue+"' tagId='"+tagId+"'></li>").appendTo(ul);
		var action=$tagdiv.data('action');
		var tagHtm=tagValue;
		tagHtm=tagHtm.replace(/ /g,"&nbsp;");
		tagHtm=tagHtm.replace(/</g,"&lt;");
		tagHtm=tagHtm.replace(/>/g,"&gt;");
		if(typeof(action)=='function'){//点击之后执行函数
			var a=$("<a href='javascript:;'><span>"+tagHtm+"</span></a>").appendTo(li);
			a.click(function(){action(tagValue,tagId);});
		}else if(typeof(action)=='object' && typeof(action.href)=='string'){//链接
			var url=action.href.replace(/%v%/g,tagValue);
			url=url.replace(/%id%/g,tagId);
			li.html("<a href='"+url+"' target='"+action.target+"'><span>"+tagHtm+"</span></a>");
		}else{//点击无动作
			li.html("<span>"+tagHtm+"</span>");
		}
		if($tagdiv.data('del')){//是否包含删除按钮
			var a=$("<a href='javascript:;' title='Delete'>x</a>").appendTo(li);
			a.click(function(){
				//删除之前执行的函数
				try{
					var onDel=$tagdiv.data('onDel');
					if(typeof(onDel)=='function'){
						//如果返回false就不删除
						if(onDel(tagValue,tagId)==false)return false;
					}
				}catch(e){return;}
				//删除
				$tagdiv.tagsDel(tagValue,tagId);
			});
		}
		//总标签数加1
		$(this).data('count',count+1);
		return true;
	},
	/**
	*删除标签（根据tagValue或者tagId进行删除，优先按照tagValue进行查找）
	*tagValue----标签内容
	*tagId-------标签id
	*/
	$.fn.tagsDel=function(tagValue,tagId){
		var $tagdiv=$(this);
		//判断全局设置中是否允许删除标签
		if(!$tagdiv.data('del'))return false;
		//标签前缀
		var tagper=$tagdiv.attr("tagname");
		if(typeof(tagper)=="undefined" || tagper=="")return false;
		//检查参数
		if(!tagValue && !tagId)return false;
		//找出对应标签的li
		var index=$tagdiv.tagsIndexof(tagValue,tagId);
		if(index==-1)return;
		var oUl=document.getElementById(tagper+"_tag_list");
		var oLis=oUl.getElementsByTagName("li");
		var li=oLis[index];
		if(!li || typeof(li)!='object')return false;
		//删除元素
		var remli=$(li).remove();
		//标签个数减1
		var count=$(this).data('count');
		$(this).data('count',count-1);
		return true;
	},
	/**
	 * 清空标签容器
	 * */
	$.fn.tagsClear=function(){
		var tagper=$(this).attr("tagname");
		$("#"+tagper+"_tag_list").empty();
	},
	/**
	 * 获取标签个数
	 */
	$.fn.tagsCount=function(){
		var tagper=$(this).attr("tagname");
		var oUl=document.getElementById(tagper+"_tag_list");
		var oLis=oUl.getElementsByTagName("li");
		if(!oLis)return 0;
		$(this).data('count',oLis.length);//修正count
		return oLis.length;
	},
	/**
	 * 获取某个标签的index
	 * 如果tagValue不为空，按照tagValue查找，否则按照tagId进行查找
	 * */
	$.fn.tagsIndexof=function(tagValue,tagId){
		if(!tagValue && !tagId)return -1;
		
		var tagper=$(this).attr("tagname");
		var oUl=document.getElementById(tagper+"_tag_list");
		var oLis=oUl.getElementsByTagName("li");
		for(var i=0;i<oLis.length;i++){
			if(tagValue!=""){
				if(tagValue==oLis[i].title)return i;
			}else{
				if(tagId==oLis[i].attr("tagId"))return i;
			}
		}
		return -1;
	},
	/**
	 * 将所有标签生成str
	 * @param split 标签之间的间隔字符或者字符串
	 * */
	$.fn.tagsStr=function(split){
		if(!split || typeof(split)!='string')split=',';
		var str="";
		var tagper=$(this).attr("tagname");
		var oUl=document.getElementById(tagper+"_tag_list");
		var oLis=oUl.getElementsByTagName("li");
		for(var i=0;i<oLis.length;i++){
			str+=oLis[i].title+split;
		}
		if(str.length>0){str=str.substring(0,str.length-split.length);}
		return str;
	},
	/**
	 * 将所有标签生成json格式
	 * */
	$.fn.tagsJson=function(){
		var json="";
		var tagper=$(this).attr("tagname");
		var oUl=document.getElementById(tagper+"_tag_list");
		var oLis=oUl.getElementsByTagName("li");
		for(var i=0;i<oLis.length;i++){
			json+='{"id":"'+$(oLis[i]).attr('tagId')+'","name":"'+oLis[i].title+'"},';
		}
		if(json.length>0){json=json.substring(0,json.length-1);}
		return '{"tags":['+json+']}';
	}
})(jQuery);
