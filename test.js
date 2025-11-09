// ==UserScript==
// @name         Virt Orig Script
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://www.pal.tech/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=pal.tech
// @grant        none
// ==/UserScript==


(function() {
    'use strict';

    // Your code here...
    let flag=false;

    let total_data=[];
    let string=JSON.stringify(total_data);

    let get_total_data=sessionStorage.getItem("data");
    let data_array = JSON.parse(get_total_data);

    let get_received_data=sessionStorage.getItem("received");
    let received_array = JSON.parse(get_received_data);


    if(data_array === null)
    {
        sessionStorage.setItem("data", string);
    }

    if(received_array === null)
    {
        sessionStorage.setItem("received",string);
    }


    var toggle=sessionStorage.getItem("open");
    if(toggle === null)
    {
        sessionStorage.setItem("open",false);
    }

    console.log('got here 1')
    let cursor=document.createElement('img');
    cursor.src='https://gitlab.pal.tech/ramakrishna.bapathu/images/-/raw/main/chatbot.jpg';
    cursor.setAttribute('id','cursor');
    console.log('got here 2')
    document.body.appendChild(cursor);
    console.log('got here 3')
    let textbox = document.createElement('div');
    textbox.setAttribute('id','textbox');
    document.body.appendChild(textbox);
    console.log('got here 4')
    let path=[];
    console.log('got here 5')
    let chatbot=document.createElement('div');
    chatbot.setAttribute('id','chatcomponent');
    console.log('got here 6')

    let chat=document.createElement('img');
    chat.src='https://static-00.iconduck.com/assets.00/chat-icon-2048x2048-i7er18st.png';
    chat.setAttribute('id','chat');
    chat.addEventListener('click', function handleClick(event) {
        // transition();
        var element= document.getElementById('chatbot-container');
        if(element.className === 'chatbot_none')
        {
            element.className = 'chatbot_flex';
            sessionStorage.setItem("open",true);
            var child=document.getElementsByClassName('button');
            for(var l=0;l<child.length;l++)
            {
                child[l].setAttribute('disabled','true');
                child[l].classList.add('disabled');
            }

            var api='http://127.0.0.1:8000/get_response';

            var conversation=document.getElementById('conversation');
            var loader=document.createElement('div');
            loader.innerHTML='Loading...';
            loader.id='loader';
            conversation.appendChild(loader);
            loader.scrollIntoView();

            fetch(api, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"message": window.location.pathname})
            })
                .then(res => res.json())
                .then(json =>{
                loader.remove();
                var conversation= document.getElementById('conversation');
                var options=json.options;
                if(options.length !== 0)
                {
                    var receive=document.createElement('div');
                    receive.className='receive';
                    var content=document.createElement('div');
                    var text="Choose one of the following options or just text in the message box";
                    content.innerHTML=text;
                    receive.appendChild(content);
                    for(var i=0;i<options.length;i++)
                    {
                        var ele=document.createElement('div');
                        ele.innerHTML=options[i];
                        ele.className='button';
                        ele.addEventListener('click', function handleClick(event){
                            var value=event.target.innerHTML;

                            let get_total_data=sessionStorage.getItem("data");
                            let data_array = JSON.parse(get_total_data);
                            if(data_array === null)
                            {
                                data_array=[];
                            }
                            data_array.push(value);
                            let string_array=JSON.stringify(data_array);
                            sessionStorage.setItem("data", string_array);


                            var send = document.createElement('div');
                            send.className='send';
                            send.innerHTML=value;
                            conversation.appendChild(send);
                            send.scrollIntoView({ behavior: "smooth", block: "end"});

                            var child=document.getElementsByClassName('button');
                            for(var l=0;l<child.length;l++)
                            {
                                child[l].setAttribute('disabled','true');
                                child[l].classList.add('disabled');
                            }



                            apicall(value);

                        });
                        receive.appendChild(ele);
                    }
                    conversation.appendChild(receive);
                    receive.scrollIntoView({ behavior: "smooth", block: "end"});
                }

            });

        }
        else
        {
            element.className = 'chatbot_none';
            sessionStorage.setItem("open",false);
        }
    });
    chatbot.appendChild(chat);

    let chatbot_container=document.createElement('div');
    chatbot_container.setAttribute('id','chatbot-container');
    chatbot_container.className='';
    if(toggle === "true")
    {
        chatbot_container.className='chatbot_flex';
    }
    else
    {
        chatbot_container.className='chatbot_none';
    }



    let header =document.createElement('div');
    header.setAttribute('id','header');

    let header_text=document.createElement('div');
    header_text.innerHTML='Virtual Assistant';

    let close_button=document.createElement('div');
    close_button.setAttribute('id','close-button');
    close_button.innerHTML='x';
    close_button.addEventListener('click', function handleClick(event) {
        var element= document.getElementById('chatbot-container');
        element.className = 'chatbot_none';
        sessionStorage.setItem("open",false);
    });

    header.appendChild(close_button);
    header.appendChild(header_text);

    let conversation_wrapper=document.createElement('div');
    conversation_wrapper.className='conversation-wrapper';

    let conversation=document.createElement('div');
    conversation.setAttribute('id','conversation');


    if(data_array !== null && data_array.length !== 0)
    {
        for(var i=0;i<data_array.length;i++)
        {
            var send = document.createElement('div');
            send.className='send';
            send.innerHTML=data_array[i];
            conversation.appendChild(send);
            send.scrollIntoView({ behavior: "smooth", block: "end"});


            var receive=document.createElement('receive');
            receive.className='receive';
            for(var k=0;k<received_array[i].length;k++)
            {
                var ele=document.createElement('div');
                ele.innerHTML=received_array[i][k];
                if(received_array[i][k] === '&#8595;')
                {
                    ele.className='arrow';
                }
                receive.appendChild(ele);
                if(k === 0)
                {
                    var nav=document.createElement('div');
                    nav.className='button disabled';
                    nav.innerHTML="Navigate";
                    receive.appendChild(nav);
                }

            }

            conversation.appendChild(receive);
            receive.scrollIntoView({ behavior: "smooth", block: "end"});
        }
    }



    conversation_wrapper.appendChild(conversation);

    let footer=document.createElement('div');
    footer.setAttribute('id','footer');

    let input_ele=document.createElement('input');
    input_ele.setAttribute('type','text');
    input_ele.setAttribute('placeholder','Message');
    input_ele.setAttribute('id','chat_value');
    input_ele.addEventListener("keydown", function handleClick(event){
        if(event.key === 'Enter')
        {
            SendMessage();
        }

    });

    let send_icon=document.createElement('img');
    send_icon.src='https://gitlab.pal.tech/ramakrishna.bapathu/images/-/raw/main/send.jpg';
    send_icon.setAttribute('id','send');
    send_icon.addEventListener('click', function handleClick(event){
        SendMessage();
    });

    function SendMessage()
    {
        var child=document.getElementsByClassName('button');
        for(var l=0;l<child.length;l++)
        {
            child[l].setAttribute('disabled','true');
            child[l].classList.add('disabled');
        }
        var value=document.getElementById('chat_value').value;

        let get_total_data=sessionStorage.getItem("data");
        let data_array = JSON.parse(get_total_data);
        if(data_array === null)
        {
            data_array=[];
        }
        data_array.push(value);
        let string_array=JSON.stringify(data_array);
        sessionStorage.setItem("data", string_array);

        //  var element= document.getElementById('chatbot-container');
        //   element.className = 'chatbot_none';

        var send = document.createElement('div');
        send.className='send';
        send.innerHTML=value;
        conversation.appendChild(send);
        send.scrollIntoView({ behavior: "smooth", block: "end"});

        apicall(value);

        document.getElementById('chat_value').value='';

    }


    footer.appendChild(input_ele);
    footer.appendChild(send_icon);




    chatbot_container.appendChild(header);
    chatbot_container.appendChild(conversation_wrapper);
    chatbot_container.appendChild(footer);

    chatbot.appendChild(chatbot_container);

    document.body.appendChild(chatbot);



    function apicall(value)
    {
        var api='http://localhost:8000/get_response';

        var conversation=document.getElementById('conversation');
        var loader=document.createElement('div');
        loader.innerHTML='Loading...';
        loader.id='loader';
        conversation.appendChild(loader);
        loader.scrollIntoView();

        fetch(api, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"message": value})
        })
            .then(res => res.json())
            .then(json =>{
            // console.log(json);
            loader.remove();

            var kb_resp = json.response.output;
            path=json.path;
            // console.log("path", path)

            var receive=document.createElement('div');
            receive.className='receive';
            var elem=document.createElement('div');
            elem.innerHTML=kb_resp;

            var temp=[];
            temp.push(kb_resp);

            var navigate = document.createElement('div');
            navigate.className='button';
            navigate.innerHTML='Navigate';
            navigate.addEventListener('click', function handleClick(event){
                var disabled=navigate.getAttribute('disabled');
                if(!disabled)
                {
                    if(flag)
                    {
                        var ele2=document.createElement('div');
                        ele2.innerHTML="The path goes like the following:";
                        receive.appendChild(ele2);
                        temp.push("The path goes like the following:");
                        for(var i=0;i<path.length;i++)
                        {
                            var ele=document.createElement('div');
                            ele.innerHTML=path[i].Category;
                            receive.appendChild(ele);

                            temp.push(path[i].Category);
                            if(i !== path.length -1)
                            {
                                var ele1=document.createElement('div');
                                ele1.innerHTML='&#8595;';
                                ele1.className='arrow';
                                receive.appendChild(ele1);

                                temp.push('&#8595;');
                            }
                        }

                    }
                    else
                    {
                        var ele3=document.createElement('div');
                        ele3.innerHTML="I am always around to assist you further";
                        receive.appendChild(ele3);
                        temp.push("I am always around to assist you further");
                    }
                    received_array.pop();
                    received_array.push(temp);
                    sessionStorage.setItem("received",JSON.stringify(received_array));

                    navigate.setAttribute('disabled','true');
                    navigate.classList.add('disabled');
                    receive.scrollIntoView({ behavior: "smooth", block: "end"});

                    custom();
                    transition();


                }

            });


            receive.appendChild(elem);

            receive.appendChild(navigate);


            if(received_array === null)
            {
                received_array=[];
            }

            received_array.push(temp);
            sessionStorage.setItem("received",JSON.stringify(received_array));
            conversation.appendChild(receive);
            receive.scrollIntoView({ behavior: "smooth", block: "end"});

        })

    }

    let animation_delay = 450;

    function transition(){

        changePosition(path[0].ID,path[0].Category);
        recursive(path[0],1);

    }

    function recursive(element,next)
    {
        setTimeout(()=>{

            let ele=document.getElementById(element.ID);
            ele.style.transform="scale(0.98)";
            ele.style.boxShadow='3px 2px 22px 1px #d49b54';

            setTimeout(()=>{

                if(element.CategoryType === 'Hover')
                {

                    if(element.Category === 'What We Do')
                    {
                        let child=ele.getElementsByClassName('sub-menu')[0];
                        child.style.display='block';

                        let wrap=ele.getElementsByClassName('wrap')[0];
                        let wrap_child=wrap.childNodes;

                        for(var c=0;c<wrap_child.length;c++)
                        {
                            if(wrap_child[c].nodeType === 1)
                            {
                                wrap_child[c].classList.remove('active');
                            }
                        }
                    }
                    else
                    {
                        ele.classList.add('active');

                        ele.getElementsByClassName('sub-menu')[0].classList.add('active');
                    }

                }
                else if('PagePth' in element)
                {
                    window.location.replace(element.PagePth);
                }

                ele.style.boxShadow='';
                ele.style.transform='';

            },[500]);



            if(path.length > next)
            {

                setTimeout(()=>{

                    changePosition(path[next].ID,path[next].Category);
                    recursive(path[next],next+1);

                },[600]);

            }
            else
            {
                return;
            }



        },[animation_delay]);
    }

    function changePosition(ID, content)
    {
        let string_time = animation_delay / 1000;

        let cursor = document.getElementById("cursor");
        cursor.style.visibility = "visible";
        cursor.style.transition = "all " + string_time + "s linear";

        let text = document.getElementById("textbox");
        text.style.visibility = "visible";
        text.style.transition = "all " + string_time + "s linear";

        let element=document.getElementById(ID);
        var rect = element.getBoundingClientRect();

        cursor.style.left = rect.left + 10 + "px";
        cursor.style.top = rect.top + 10 + "px";

        text.style.left = rect.left - 10 + "px";
        text.style.top = rect.top + "px";
        text.innerHTML = "Moving to "+content;
    }

    function custom()
    {
        const chat=document.getElementById('chat');
        var rect = chat.getBoundingClientRect();

        let cursor = document.getElementById("cursor");
        cursor.style.visibility='hidden';
        cursor.style.left = rect.left + "px";
        cursor.style.top = rect.top + "px";

        let textbox = document.getElementById("textbox");
        textbox.style.visibility='hidden';
        textbox.style.left = rect.left + "px";
        textbox.style.top = rect.top + "px";
    }



    let customStyle=document.createElement('style');
    let customCSS= `
#cursor{
   pointer-events: none;
   position: fixed;
   width: 70px;
   height: 70px;
   z-index: 2000;
   display: block;


}
#textbox{
position: fixed;
background-color: black;
color: white;
z-index: 2000;
padding: 5px;
}
#chatcomponent{
  width: 50px;
  height: 50px;
  border-radius: 50%;
  position: fixed;
  bottom: 10%;
  right: 5%;
  cursor: pointer;
  z-index: 100;
}
#chat{
width: 50px;
}

#chatbot-container{
 box-shadow: 0px 0px 6px #00000029;
position: absolute;
right: 5%;
bottom: calc(100% + 10px);
width: 400px;
height: 60vh;
max-width: 400px;
min-height: 400px;
background-color: white;
border-radius: 25px;

flex-direction: column;
gap: 15px;

background-color: #0177da;
}
.chatbot_flex{
display: flex;
}
.chatbot_none{
display: none;
}

#header{
  display: flex;
flex-direction: column;
justify-content: center;
align-items: center;
color: white;
position: absolute;
top: 0%;
left: 0%;

width: 100%;
}
#close-button{
align-self: flex-end;
position: relative;
right: 5%;
cursor: pointer;
}


.conversation-wrapper{
  background-color: #f1f2f6;
height: 85%;
top: 15%;
border-bottom-left-radius: 25px;
border-bottom-right-radius: 25px;
display: flex;
flex-direction: column;
overflow: auto;
position: relative;
padding: 4px;
}
#conversation{
background-color: #f1f2f6;
height: 85%;
border-bottom-left-radius: 25px;
border-bottom-right-radius: 25px;
display: flex;
flex-direction: column;
overflow: auto;
overflow-x: hidden;
position: relative;
}
#footer{
  display: flex;
width: 100%;
z-index: 1;
padding-left: 10px;
padding-right: 10px;
position: relative;
}
input{
width: 89%;
border: 1px solid #0177da;
border-radius: 8px;
padding: 8px;
}
input:focus-visible{
outline: none;
}
#send{
height: 30px;
}
.send {
align-self: flex-end;
margin: 2%;
width: -moz-fit-content;
width: fit-content;
max-width: 350px;
background-color: #0177daba;
border-radius: 10px;
color: white;
padding: 8px;
padding-left: 10px;
padding-right: 10px;
font-size: 14px;
}
.receive{
  align-self: flex-start;
margin: 2%;
width: -moz-fit-content;
width: fit-content;
max-width: 350px;
background-color: white;
border-radius: 10px;
color: #42506c;
padding: 8px;
padding-left: 10px;
padding-right: 10px;
font-size: 14px;

  display: flex;
  flex-direction: column;
  gap: 2px;
}
#conversation::-webkit-scrollbar{
 width: 4px;
}
#conversation::-webkit-scrollbar-thumb {
  background: grey;
  border-radius: 10px;
}
.arrow{
 position: relative;
 left: 30%;
}
.button{
  box-shadow: 0px 0px 6px #00000029;
    max-width: 340px;
    text-align: center;
    cursor: pointer;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid transparent;
    align-self: center;
    margin: 10px;
    display: flex;
    min-width: 130px;
    justify-content: center;
}
.disabled{
        background-color: #80808061;
        color: white;
        padding: 5px;
        cursor: not-allowed;
}
#loader{
 text-align: center;
}
`;
    customStyle.appendChild(document.createTextNode(customCSS));
    document.head.appendChild(customStyle);


    conversation.scrollTo(0, conversation.scrollHeight);
    //console.log('Worked');

})();