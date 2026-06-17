const events = [
{
time:"78:42",
type:"GOAL",
text:"Dybala converts penalty"
},
{
time:"77:35",
type:"VAR",
text:"Possible offside"
},
{
time:"75:18",
type:"SUB",
text:"El Shaarawy replaces Pellegrini"
},
{
time:"72:04",
type:"YELLOW",
text:"Late challenge"
},
{
time:"68:33",
type:"GOAL",
text:"Lukaku equalises"
}
];

const container =
document.getElementById("events");

events.forEach(e => {

container.innerHTML += `
<div class="event">

<div class="time">
${e.time}
</div>

<div class="etype">
${e.type}
</div>

<div class="desc">
${e.text}
</div>

</div>
`;

});