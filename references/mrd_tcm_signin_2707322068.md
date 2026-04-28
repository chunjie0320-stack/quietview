npm error errno -13
npm error EACCES: permission denied, mkdir '/root/.npm/_cacache/content-v2/sha1/83/e8'
npm error File exists: /root/.npm/_cacache/content-v2/sha1/83/e8
npm error Remove the existing file and try again, or run npm
npm error with --force to overwrite files recklessly.
npm error A complete log of this run can be found in: /root/.npm/_logs/2026-04-24T02_54_49_022Z-debug-0.log
[0;31m❌ 版本升级失败[0m
文档标题：《【MRD】中医签到组件》
文档ID：2707322068
内容长度：49086 字符

============================================================
文档内容：
============================================================

:::title{nodeId="d2c206d683ee443d87913ab0b8ce6aba"}
【MRD】中医签到组件
:::

:::catalog{style="none" nodeId="97b73f42a1eb4a7fb8adb3164d60be1a"}:::

:::heading{level=1 nodeId="99c3ec35506b4817accff6dff7b2faa0"}
一.版本记录
:::

:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="405c7390cd834a1ca4fd193d5e8ca8d5"}
:::table_row{nodeId="1017b957c4cf4a40be14fbde5d42ef73"}
:::table_header{colwidth="109" numCell=false nodeId="412466fdf21a48aab6da79b22fd031ff"}
:::paragraph{nodeId="1af846a4026b48d19c540eeff7b03b59"}
版本
:::
:::
:::table_header{colwidth="136" numCell=false nodeId="208a219a182241d7b8454dd0960ecb6d"}
:::paragraph{nodeId="6d4c3c5ee8cb47638f8e3badcfd0c574"}
修改时间
:::
:::
:::table_header{colwidth="305" numCell=false nodeId="eef8d1cb4b6e4e5ebb2267d785bdacef"}
:::paragraph{nodeId="e9b3c32f4fb0487198743a03e6836c0b"}
修改描述
:::
:::
:::table_header{colwidth="198" numCell=false nodeId="09a00c1ade1541419534dbd91db2b15f"}
:::paragraph{nodeId="295deab61dbc46f88abbd62bfaca65aa"}
提需人
:::
:::
:::
:::table_row{nodeId="2590de9264df4016becdecd9533b62e0"}
:::table_cell{colwidth="109" numCell=false nodeId="bfd98aaccbdd42a886933dbf491d86b6"}
:::paragraph{nodeId="90c809030a9343dd87df43ffcf5c2a65"}:::
:::
:::table_cell{colwidth="136" numCell=false nodeId="cf15185664c64d77bd3d53508e8f58b6"}
:::paragraph{nodeId="1bb6a4cabf77474a8a73d984430d27ee"}:::
:::
:::table_cell{colwidth="305" numCell=false nodeId="0b396777fd794cb0ab47d68bab8897e7"}
:::paragraph{nodeId="992df9e09ced41ce8c8f9396ee45c7d8"}:::
:::
:::table_cell{colwidth="198" numCell=false nodeId="c1300cccce94430ba2e3493b68970fd1"}
:::paragraph{nodeId="8b51ac6be2784dea8bec617a54779b4d"}
sunni03
:::
:::
:::
:::

:::paragraph{nodeId="31e3373add8147ca9a62dec2cf1c2e2c"}:::

:::heading{level=1 nodeId="4522b288972c4464b03953df9d1b4699"}
二.需求背景
:::

:::heading{level=2 nodeId="93632f6b55d2467696cfc30cff7bbfab"}
**1.25年中医活动签到概述**
:::

:::paragraph{nodeId="f1d048628d7a4899b9bd19d82ed7e276"}
25年中医业务核心围绕“24节气”开展了9场养生活动，精准渗透目标人群，打造了美团中医“24节气young生局”活动IP，通过“节气签到”玩法持续沉淀高粘性用户至企微社群。经25年测试验证，**__“节气签到”可有效促进用户活动参与积极性，整体提升用户粘性，有效推动用户意向转化与长效运营。__**25年中医节气签到表现如下：
:::

:::paragraph{nodeId="32024a39ffb04bf6ab80e34b5388f97e"}
**1）签到人数：**25年签到用户28,905人；
:::

:::paragraph{nodeId="4fd0f017377d4a8caa3d59dd160d2e07"}
**2）新客表现：**新客:[footnote]{id="3bae4c83-bb9c-4237-bf64-56756248ac5d" annotate="" nodeId="f39526a2526844ee83e3b366954a441d"}数为23,616人，新客占比81.7%；
:::

:::paragraph{nodeId="0c9c0c07829e491a83ec97425c7a79db"}
**3）复购表现：**新客复购:[footnote]{id="1f818428-d5c7-45ee-baa7-798718eafb9e" annotate="" nodeId="cc5fcd7546324939ad42cb893446b993"}人数为567人，复购率达2.4%；
:::

:::paragraph{nodeId="4bfdac1f3b1b43c686414134c9148615"}
**4）累计签到：**累计签到2次共2,044人，占比70.4%；累计签到4次共647人，占比2.2%；累计签到6次共340人，占比1.2%；
:::

:::paragraph{nodeId="db7ccb1c798f4da4aebf480dea3f922f"}
**5）用户反馈：**签到且收到实物礼的用户会自发于小红书、企微活动社群进行奖品和养生故事的分享
:::

:::collapse{nodeId="1b408d31c7d94af38fe5c528ff0b648d" titleNodeId="3db2b2619552403981239f463083866a" contentNodeId="a98bd6ee33d74b4b84a9f3af687f64cc"}
25年签到路径说明
---
:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="7e95849c08e64dfcbed930ba40ea071f"}
:::table_row{nodeId="71e8dfabaa114f30ac8732638214de36"}
:::table_header{colwidth="80" numCell=false nodeId="16053164449a44f9ac6f05634ce1c13b"}
:::paragraph{nodeId="97d3688053904cb6b2927e1794e10bcd"}:::
:::
:::table_header{colwidth="210" numCell=false nodeId="0e7bd0ec0a3c452d93aed83bfa776d77"}
:::paragraph{nodeId="11540622944e4159ba1742dbe52dd53b"}
**步骤说明**
:::
:::
:::table_header{colwidth="268" numCell=false nodeId="739e17bfda8243e783313e07f7148e68"}
:::paragraph{nodeId="53d18e95077f4097b9657acb1a7815bf"}
**目前实现方式**
:::
:::
:::table_header{colwidth="121" numCell=false nodeId="32b3955ab56b44a38837c2a28ea2f08d"}
:::paragraph{nodeId="cb3a1d42b601419fa2595763aaab146d"}
**示意图**
:::
:::
:::table_header{colwidth="665" numCell=false nodeId="d1c8fd08cfdb46d5a93c6108a3753eba"}
:::paragraph{nodeId="560edd12d57c4bb2b9bec7b44fd4074f"}
**签到完整链路图**
:::
:::
:::
:::table_row{nodeId="d4e0b88aff00486787302af436e04b03"}
:::table_cell{colwidth="80" verticalAlign="middle" numCell=false nodeId="5097a60014b24ea180b0bbdc8fe72683"}
:::paragraph{nodeId="b297a6de7929427cb21a5b2552c280ec"}
:[font]{size=13}**默认态**[/font]
:::
:::
:::table_cell{colwidth="210" verticalAlign="middle" numCell=false nodeId="0be72b7e3a0b4dd799af197cf7207ca1"}
:::paragraph{nodeId="6397cc3cd84a47d3abc27725eb25e4da"}
:[font]{size=13}节气日历签到提示[/font]
:::
:::
:::table_cell{colwidth="268" verticalAlign="middle" numCell=false nodeId="838dc92d24904b80b0eb5f2f0b808f26"}
:::paragraph{nodeId="66c477c98efd45fe8c425a48bc3a57fe"}
:[font]{size=13}通过图片组件，9x9定位搭建节气签到框架[/font]
:::

:::paragraph{nodeId="f4c69dadf6ba405b934bd6b11632e929"}
:[font]{size=13}以右图为例：[/font]
:::

:::bullet_list{indent=0 nodeId="05bda6110cd5469cbbe0d777af39c7d4"}
:::list_item{level=0 hidden=false fontSize=13 nodeId="dcb28f4d0c94460dbf850026a6abb169"}
:::paragraph{nodeId="48aafc0f3941449bbc29e9e991dc89e2"}
:[font]{size=13}绿色卡片代表本次签到；[/font]
:::
:::
:::

:::bullet_list{indent=0 nodeId="72e14de41d7844479cd48a7437e0cd41"}
:::list_item{level=0 hidden=false fontSize=13 nodeId="76d55a566b9e4b2e8a2d3fa56b8f81b5"}
:::paragraph{nodeId="d4c957a8467c416397636665ee0031b5"}
:[font]{size=13}灰色卡片代表不可签到；[/font]
:::
:::
:::list_item{level=0 hidden=false fontSize=13 nodeId="6e210e1840084c37bcecd314f7acdce8"}
:::paragraph{nodeId="015b170f6e03463681f53520e8133c16"}
:[font]{size=13}黄色卡片代表待开放签到[/font]
:::
:::
:::
:::
:::table_cell{colwidth="121" verticalAlign="middle" numCell=false nodeId="85fafa13d1294ad69eb196e46d2ac559"}
:::paragraph{nodeId="af2da5c055df405d95e6bfbd3720947c"}
![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218396997820?contentType=1){width=160 height=216 small="https://km.sankuai.com/api/file/cdn/2707322068/218396997820?contentType=1" origin="https://km.sankuai.com/api/file/cdn/2707322068/218396997820?contentType=1" nodeId="fdbcdec264ba4a8cb14615ba2111cc96"}
:::
:::
:::table_cell{rowspan=4 colwidth="665" numCell=false nodeId="d4df5b9fdfc64665b3d96d60602feabf"}
:::drawio{src="https://km.sankuai.com/api/file/cdn/2707322068/218396440501?contentType=0" width=644 height=544 nodeId="b6a12755d20f4f0e97c31d5d2b43aca3"}:::
:::
:::
:::table_row{nodeId="48426c0185af4cbf8462db5bcad46c1c"}
:::table_cell{colwidth="80" verticalAlign="middle" numCell=false nodeId="3b318c9ad2b34aa89a84fa9e2d9d0139"}
:::paragraph{nodeId="3ac950be7630462b90a014ed5a555b77"}
:[font]{size=13}**STEP1**[/font]
:::
:::
:::table_cell{colwidth="210" verticalAlign="middle" numCell=false nodeId="1ff8f355fb4c40e5bbebb05197f9c34b"}
:::paragraph{nodeId="126e235877704cffa526a24e8eb0a781"}
:[font]{size=13}点击绿色卡片[/font]
:::
:::
:::table_cell{colwidth="268" verticalAlign="middle" numCell=false nodeId="49a5c539eb3e4db79e070c16370777cd"}
:::paragraph{nodeId="7fd80838d5554b1daa05d6ae2a04671f"}
:[font]{size=13}图片组件附带跳转链接，实现页面二跳[/font]
:::
:::
:::table_cell{colwidth="121" verticalAlign="middle" numCell=false nodeId="755ef78ac8e941dcbb692448118526d8"}
:::paragraph{nodeId="cc4c36df14404ffabe197fc266bdf416"}
![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218395445228?contentType=1){width=155 height=205 small="https://km.sankuai.com/api/file/cdn/2707322068/218395445228?contentType=1" origin="https://km.sankuai.com/api/file/cdn/2707322068/218395445228?contentType=1" nodeId="6617c4748aa649079d73de5392e3c676"}
:::
:::
:::
:::table_row{nodeId="10f4caa75def4f30b97f121eba1937a3"}
:::table_cell{colwidth="80" verticalAlign="middle" numCell=false nodeId="174ad80b29f1447d9b8168241fe8f7f4"}
:::paragraph{nodeId="3c74674def4d44368a38b5163216477e"}
:[font]{size=13}**STEP2**[/font]
:::
:::
:::table_cell{colwidth="210" verticalAlign="middle" numCell=false nodeId="299ab4f263d84f5884e68b16fca45038"}
:::paragraph{nodeId="14bf067c98b74814925b3f6720f142a3"}
:[font]{size=13}进入二跳页面[/font]
:::

:::paragraph{nodeId="b48323b11e684030ada8dbec1e696298"}
:[font]{size=13}点击领券按钮[/font]
:::

:::paragraph{nodeId="8a4d1b716c5c45bdbf4b6a199c8427d7"}
:[font]{size=13}通过领券动作记录签到用户userid[/font]
:::
:::
:::table_cell{colwidth="268" verticalAlign="middle" numCell=false nodeId="c2bff4b413804ee99bf8d6a600af3cfc"}
:::paragraph{nodeId="350a3e631cb34859845fef687ec6e7b8"}
:[font]{size=13}领券组件记录领券userid[/font]
:::
:::
:::table_cell{colwidth="121" verticalAlign="middle" numCell=false nodeId="90b7b4bc586b47fca92259407d4e3525"}
:::paragraph{nodeId="931e2def59284260bc546c9a547d54f0"}
![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218395978826?contentType=1){width=157 height=210 small="https://km.sankuai.com/api/file/cdn/2707322068/218395978826?contentType=1" origin="https://km.sankuai.com/api/file/cdn/2707322068/218395978826?contentType=1" nodeId="30ac572c8bb54bce858e10a330233203"}
:::
:::
:::
:::table_row{nodeId="f8f474d5abb84a27b251d3a2e5774ed4"}
:::table_cell{colwidth="80" verticalAlign="middle" numCell=false nodeId="de53c0cf45854499a4127f2a2ccef94d"}
:::paragraph{nodeId="fdf079f9e3bf4b3ebad84ac045ae591e"}
:[font]{size=13}**STEP3**[/font]
:::
:::
:::table_cell{colwidth="210" verticalAlign="middle" numCell=false nodeId="befe9c2419a04afe95c368d393eacb79"}
:::paragraph{nodeId="05adef45b62d40258de89c51eb51c206"}
:[font]{size=13}用户填写姓名、电话、收货地址[/font]
:::

:::paragraph{nodeId="f5d7bf4ff66f48ec857c648d1cd362b5"}
:[font]{size=13}方便运营人员联系用户[/font]
:::

:::paragraph{nodeId="54fd3606720f4fba9556f88901e76d02"}
:[font]{size=13}完成实物奖品的发放[/font]
:::
:::
:::table_cell{colwidth="268" verticalAlign="middle" numCell=false nodeId="47b4566bbece4e958c760eccaa92a5c9"}
:::paragraph{nodeId="3e7802b058b14778ab891eb8978b8c70"}
:[font]{size=13}留资组件[/font]
:::
:::
:::table_cell{colwidth="121" verticalAlign="middle" numCell=false nodeId="74d0c6c334ca49cb8dad19833389ed6a"}
:::paragraph{nodeId="c9120abd1ed34f9eaa39fea7ef0e48c5"}
![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218396063982?contentType=1){width=321 height=453 small="https://km.sankuai.com/api/file/cdn/2707322068/218396063982?contentType=1" origin="https://km.sankuai.com/api/file/cdn/2707322068/218396063982?contentType=1" nodeId="3afe5a66f24942a2b77aca3830c12b70"}
:::
:::
:::
:::
:::

:::collapse{nodeId="7599d7cd55814478abd0a87c426ab57c" titleNodeId="2c4a67de524a452096323cfcaf286497" contentNodeId="2a8d5625b3af4fabb532526dbeb23044"}
:[font]{size=15}每场节气活动签到明细[/font]
---
:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="eba0d80d07e34991884aa760644361f4"}
:::table_row{nodeId="88e7177fe91d43f4a2bbb37830884c80"}
:::table_header{colwidth="186" numCell=false nodeId="2f5a2eb13fcf405bb6e4c83875cb182d"}
:::paragraph{align="center" nodeId="6825d39d277e4951b5d99f158a7dbd2a"}
活动
:::
:::
:::table_header{colwidth="117" numCell=false nodeId="6efd853f03a44b08a78438ac94020607"}
:::paragraph{align="center" nodeId="0bf33aa207774e85a3d23e2d6af067e4"}
签到人数
:::
:::
:::table_header{colwidth="304" numCell=false nodeId="3564477ee6a24b179c0067bc407989cb"}
:::paragraph{align="center" nodeId="4ee18e262233404185f176bdd1c7f957"}
userid表格
:::
:::
:::table_header{colwidth="194" numCell=false nodeId="d13a839e36fc4253aabd9d28467b2fdd"}
:::paragraph{align="center" nodeId="1ddedf2c08e343b9b9d7a4524783debb"}
签到玩法ID
:::
:::
:::
:::table_row{nodeId="1a160a9037764827bbe579687349a291"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="9d9ddcafa1a949d0b6806458cf5f29d8"}
:::paragraph{align="center" nodeId="25e3361b54de4486a6034134828a8fc0"}
:[font]{size=13}春分（3.13-3.27）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="3bc8313f4f4c438ab31c7cc15104518d"}
:::paragraph{align="center" nodeId="9a2c722c9b21419bb2d96526ec47d155"}
:[font]{size=13}4,252[/font]
:::
:::
:::table_cell{colwidth="304" verticalAlign="middle" numCell=false nodeId="60ebd089c9a741309ee8c19d2447756d"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218375053717?contentType=0" name="春分领券userid.xlsx" size="230.82KB" nodeId="4ff930474b5c446890e34bd5eabe5fb5"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="61888c2fe69b4ddd8f2ea7c1344f1d61"}
:::paragraph{nodeId="0d00b0a0bef24ee1968cb6cdd415579e"}
6cbc883e8b
:::

:::collapse{nodeId="269417bde8bc4bb3b52c35271540a29c" titleNodeId="c0f287b227a64731a478df4881631ddd" contentNodeId="d7b93f01804b43aeabaa255624243f37"}
sql
---
:::paragraph{nodeId="0a42e7f0adb84d16af312739b345f039"}
SELECT _mt_datetime,usertype,userid,sourceactivityid,taskkeys
:::

:::paragraph{nodeId="3bb89397712046e39176383d95f6fc98"}
FROM  log.cube_task_center_oplog
:::

:::paragraph{nodeId="e11a22bd11ab40c88c856ab912372c35"}
WHERE task keys='6cbc883e8b'
:::

:::paragraph{nodeId="02a995fe1bcd46d68eb7aa9711f330f8"}
and code = 0
:::
:::
:::
:::
:::table_row{nodeId="f0cde947d93d46c49dc45b14ff4a10c6"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="3e298ad6e180425383637d74398691c9"}
:::paragraph{align="center" nodeId="cd93f6b5f51841d3af16e781af836603"}
:[font]{size=13}谷雨（4.15-4.25）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="b36597d736b64c9e8e4174b9c93cbe1d"}
:::paragraph{align="center" nodeId="d3834a669ca94e02bd6eea17f8b640d7"}
:[font]{size=13}4,353[/font]
:::
:::
:::table_cell{colwidth="304" verticalAlign="middle" numCell=false nodeId="8dea8562754e4ff08ae3de235b12a36d"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218376563386?contentType=0" name="端午领券userid.xlsx" size="1.01MB" nodeId="215f89358c6649f5ab00e193e98dbf14"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="04fd7ac75c4b447eadc821daf61ac53d"}
:::paragraph{nodeId="1f93010e0edd4a06b0872076d0f7360d"}
144089
:::
:::
:::
:::table_row{nodeId="2d050e94865e48809e2b26879f8b6c66"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="cf6bc82e2a0e4f8eb664ca5625271d5d"}
:::paragraph{align="center" nodeId="363d5e0d7fa040fb9b51f14e4d3d769f"}
:[font]{size=13}端午（5.24-6.7）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="d696f39b123c40a0b528135001d9fccf"}
:::paragraph{align="center" nodeId="78a67bece28342da9a92f38c6376cb5f"}
:[font]{size=13}6,274[/font]
:::
:::
:::table_cell{colwidth="304" verticalAlign="middle" numCell=false nodeId="76d8ce824a574ba08f568715b335e77c"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218375449834?contentType=0" name="谷雨领券userid.xlsx" size="1.36MB" nodeId="4820e945b23a441897e41c957127419a"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="ddda5696a2a64ab1a90d781db428602c"}
:::paragraph{nodeId="13f88a8d7d0443cfb6cf31212dfb9471"}
148115
:::
:::
:::
:::table_row{nodeId="91a334a9c637489dba8660b0afbcd538"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="9351e8549c5f434f938dbc8b9618ce7f"}
:::paragraph{align="center" nodeId="373e432af7c348bf839402e063a7e953"}
:[font]{size=13}三伏（7.13-8.17）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="79e3010d52c14215bad16d1ec3af4ace"}
:::paragraph{align="center" nodeId="24fe560d06cd4f4c9b49782a30fcec46"}
:[font]{size=13}4,458[/font]
:::
:::
:::table_cell{colwidth="304" verticalAlign="middle" numCell=false nodeId="b0359a5ad9e249a8a8dd64bea34b1211"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218377994944?contentType=0" name="三伏签到领券userid.xlsx" size="1.28MB" nodeId="c63c2c6f1a5f4eebbb8bb2da055750a4"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="0290bcd68f0640db8ecf19d94e2f636f"}
:::paragraph{nodeId="1c1af15b917e4760ab06bc1201506064"}
:[font]{size=13}154168[/font]
:::
:::
:::
:::table_row{nodeId="a1bc51e3e62e4247930ca47e203e83a6"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="3c905d74518649caa204c379300019b8"}
:::paragraph{align="center" nodeId="4e2a3455be8143a0896b2dd5624d51d4"}
:[font]{size=13}白露（8.22-9.21）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="da96ea7c1df74a3fba3cb77c8b0ce7b5"}
:::paragraph{align="center" nodeId="07f96c75b05e4549b68f9137c9bd31c5"}
:[font]{size=13}5,571[/font]
:::
:::
:::table_cell{colwidth="304" verticalAlign="middle" numCell=false nodeId="fb16a8c6eecb4077937d0cf102ea9200"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218375449833?contentType=0" name="白露领券userid.xlsx" size="72.49KB" nodeId="ab4e7ed5eb094c21838a373cdbb3c0fc"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="6d65cc9570b8480bae125e692290c03f"}
:::paragraph{nodeId="d6ef5f9090cd409aa0d64dd524117628"}
:[font]{size=13}160030[/font]
:::
:::
:::
:::table_row{nodeId="827fccbfe74140bbb10be345248d5867"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="2642fc7ca4224a2285a9d10f902e4374"}
:::paragraph{align="center" nodeId="4dfcef94c57443a2993a852f53d4e7ed"}
:[font]{size=13}霜降（10.13-10.26）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="5854e98419a04a64a19e69196ec089c8"}
:::paragraph{align="center" nodeId="5543c142f2c1479ab003cd4dacf5ca62"}
:[font]{size=13}1,491[/font]
:::
:::
:::table_cell{colwidth="304" verticalAlign="middle" numCell=false nodeId="4e7dd4db935a4ae8b22a186870752e7a"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218375568300?contentType=0" name="霜降领券userid.xlsx" size="29.21KB" nodeId="67649aa1ef6b466689870dc0cfc4c359"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="f7d26e65cdd04f74b0c3864080e43523"}
:::paragraph{nodeId="de82b651c1ad4306b14b9c1c23089d27"}
:[font]{size=13}165257[/font]
:::
:::
:::
:::table_row{nodeId="b4b8d90114d84aeeba6a5539d5370255"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="f7b22d75e44c4113ab22874189908678"}
:::paragraph{align="center" nodeId="6938002ce8254cdf8072a8488a8bbc4d"}
:[font]{size=13}立冬（11.1-11.15）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="e47be4afd38e4d6caba526523944a296"}
:::paragraph{align="center" nodeId="a975f8fd3d484239bc42dfaaf8afb48e"}
:[font]{size=13}1,314[/font]
:::
:::
:::table_cell{colwidth="304" verticalAlign="middle" numCell=false nodeId="e3f68b1c52a54ea39effe4ba12f3619a"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218375330493?contentType=0" name="立冬签到人数.xlsx" size="29.33KB" nodeId="98c7bc6b0faa4133b6d78a4af7fd7e80"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="a031d4f1ae9c4f27a0a52c0e371a3762"}
:::paragraph{nodeId="0d5e2bc3f6f64cada60cd5786f7c4622"}
:[font]{size=13}167498[/font]
:::
:::
:::
:::table_row{nodeId="0d804beda60740a0bef37a2a08421957"}
:::table_cell{colwidth="186" verticalAlign="middle" numCell=false nodeId="6e720f93d4144525a276c653b176a99a"}
:::paragraph{align="center" nodeId="47abe02f76ac4cfda3a3924237c4aa82"}
:[font]{size=13}冬至（12.16-12.26）[/font]
:::
:::
:::table_cell{colwidth="117" verticalAlign="middle" numCell=false nodeId="5a6fdeb93b1648469d1e0707854c5a60"}
:::paragraph{align="center" nodeId="092c1e368b1c400085a81a9fdc2606e8"}
:[font]{size=13}1,192[/font]
:::
:::
:::table_cell{colwidth="304" numCell=false nodeId="8134a4187f0244c4a6b5daa7c1300764"}
:::attachment{src="https://km.sankuai.com/api/file/cdn/2707322068/218376881001?contentType=0" name="冬至签到userid.xlsx" size="18.81KB" nodeId="746843a867bb46939d61b342ebad18da"}:::
:::
:::table_cell{colwidth="194" numCell=false nodeId="0e08343f567e455c95fbeb7bc842f8c8"}
:::paragraph{nodeId="241a368968f94bbabfdd7b13845a323d"}
:[font]{size=13}171541[/font]
:::
:::
:::
:::
:::

:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="4803eacb8f704d6b84bfa7b77bf5546e"}
:::table_row{nodeId="aa5519c203924324961731b12c930efa"}
:::table_header{colwidth="345" nodeId="9e54d69b1a3e488aac05399b0b0be905"}
:::paragraph{align="center" nodeId="3302f9ce421f4e48a277b1dd81941486"}
**25年签到详情页**
:::
:::
:::table_header{colwidth="784" nodeId="07b95bf305f3483d9adc605dd49faad8"}
:::paragraph{align="center" nodeId="9cb072103c5a4444a06c2458f4c0d738"}
**25年签到用户反馈**
:::
:::
:::
:::table_row{nodeId="d0a59c68a0424c868908ce38a357c584"}
:::table_cell{colwidth="345" nodeId="dbec02d923714d428afb1ba9012d02c4"}
:::drawio{src="https://km.sankuai.com/api/file/cdn/2707322068/218385569337?contentType=0&isNewContent=false" width=320 height=301 nodeId="0d31db3a4b4b4d3ea9ddcb05d57d06b1"}:::
:::
:::table_cell{colwidth="784" nodeId="08c97ec0a48940c5b61ef2ad9c1ed3d9"}
:::paragraph{nodeId="f73722d8413047229fca9707c2fcff44"}
![](https://km.sankuai.com/api/file/cdn/2707322068/218403508276?contentType=1&isNewContent=false){width=146 height=317 small="https://km.sankuai.com/api/file/cdn/2707322068/218403508276?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218403508276?contentType=1&isNewContent=false" nodeId="cf048906754049cc8afd80e73cf73412"}![](https://km.sankuai.com/api/file/cdn/2707322068/218402908472?contentType=1&isNewContent=false){width=146 height=316 small="https://km.sankuai.com/api/file/cdn/2707322068/218402908472?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218402908472?contentType=1&isNewContent=false" nodeId="e93fbe5beebb43c78946ecba2a6fac21"}![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218656817815?contentType=1&isNewContent=false){width=274 height=304 small="https://km.sankuai.com/api/file/cdn/2707322068/218656817815?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218656817815?contentType=1&isNewContent=false" nodeId="f6e343c6074a4e528b3376113866ea9b"}![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218403399192?contentType=1&isNewContent=false){width=177 height=312 small="https://km.sankuai.com/api/file/cdn/2707322068/218403399192?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218403399192?contentType=1&isNewContent=false" nodeId="935466d82beb414f8551a57592b52414"}
:::
:::
:::
:::

:::heading{level=2 nodeId="03f5a6a9800a40c496cb2e12ca5b153e"}
2.签到问题反馈*
:::

:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="b38d50d01f8b42709be06b54873ba95c"}
:::table_row{nodeId="79109858e8fc468385f46006b5f04913"}
:::table_header{colwidth="73" nodeId="6d352931b85947abb2d8d5b5e2361148"}
:::paragraph{nodeId="63e6c8fc2c7a4bc1b9134ef9a38a27c3"}:::
:::
:::table_header{colwidth="765" nodeId="6a3da4ca6fe249cf9c49e7d932c36542"}
:::paragraph{nodeId="9706d623f84949beb71afdbaae239c91"}
**问题反馈**
:::
:::
:::table_header{colwidth="359" nodeId="b112a269b6794247bb61feedb0b7402d"}
:::paragraph{nodeId="2cee089f6246494c9f130658d51c445c"}
**反馈示例图**
:::
:::
:::
:::table_row{nodeId="2a8000cf6ceb40c2a2617408385ddf8e"}
:::table_cell{rowspan=3 colwidth="73" verticalAlign="middle" nodeId="55f9244ed873461a9116987842811c72"}
:::paragraph{nodeId="8b755c097c48421b9efaa7a354ef39ff"}
**运营侧**
:::
:::
:::table_cell{colwidth="765" verticalAlign="middle" nodeId="59aa433bd0c34a14bb7b35ca67e7123c"}
:::paragraph{nodeId="bfd5e9c1373843b79b572660d3fe4db5"}
1.搭建繁琐：为实现跨周期签到，目前至少需要__图片组件x9、领券组件、留资组件__
:::
:::
:::table_cell{rowspan=3 colwidth="359" nodeId="febd5db0dc064070a6ab532c4bcd18ec"}
:::paragraph{nodeId="835723db462b4066b9173cf1daa439a2"}
![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218669305675?contentType=1&isNewContent=false){width=106 height=137 small="https://km.sankuai.com/api/file/cdn/2707322068/218669305675?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218669305675?contentType=1&isNewContent=false" nodeId="808bd0d698504b558fa60db287c35bd8"}​
:::
:::
:::
:::table_row{nodeId="5de43f813a5e493caedea51ecf98308d"}
:::table_cell{colwidth="765" verticalAlign="middle" numCell=false nodeId="dc468cc723f245d5a026fa97d4fb3566"}
:::paragraph{nodeId="54b93b8707b142aaada34ebd2072323c"}
2.功能无法关联：领券组件仅支持领券功能，无法记录用户收货信息
:::
:::
:::
:::table_row{nodeId="82f6d169548149fdb86701e79b82b2f9"}
:::table_cell{colwidth="765" verticalAlign="middle" nodeId="0cde9ceac984445997bba1f6123db5e7"}
:::paragraph{nodeId="c7e6fd1e9d4f4fd382d073ea3502d7bc"}
3.数据统计困难：因组件数据无法连载，每场活动均为人工数据统计，数据庞大，易混淆搞错，影响用户体验；
:::

:::paragraph{nodeId="1b3d145103dc4f3fbfb60c786dfce56b"}
签到情况人工查询耗费大量人力、时效
:::
:::
:::
:::table_row{nodeId="d885b2956f9b4bd091ffe5878eef3f0c"}
:::table_cell{rowspan=2 colwidth="73" verticalAlign="middle" nodeId="73eb32ab21a94eeda4bf5086b1004930"}
:::paragraph{nodeId="011dc340848d4b198220f8811754282a"}
**用户侧**
:::
:::
:::table_cell{colwidth="765" verticalAlign="middle" nodeId="be3f3cc90d7d47c59142a6db119633e0"}
:::paragraph{nodeId="1c0de3ebf436449fb1e27bff820166ad"}
现有组件因无法做到跨周期数据关联，**无法满足用户以下需求：**
:::

:::paragraph{nodeId="fa925387086e4c30a1856fce6ee5304f"}
**1）自主查询签到次数及签到成功与否情况；**
:::

:::paragraph{nodeId="7cf64429bcc344cd9479f455284af394"}
**2）自主查询签到次数所对应的奖品信息、奖品物流情况；**
:::

:::paragraph{nodeId="3699564bb3c44743bd6b2ad1cedf6b05"}
**TT工单频繁进线**
:::
:::
:::table_cell{colwidth="359" nodeId="48b880c3780340f790e0fd9d2520104a"}
:::paragraph{nodeId="5d2691452a9f49e7b22e8b131554733a"}
![image.png](https://km.sankuai.com/api/file/cdn/2707322068/219744611846?contentType=1&isNewContent=false){width=86 height=121 small="https://km.sankuai.com/api/file/cdn/2707322068/219744611846?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/219744611846?contentType=1&isNewContent=false" nodeId="b67532f5d5734a44a4ca077e76e7bc3e"}![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218668910222?contentType=1&isNewContent=false){width=98 height=121 small="https://km.sankuai.com/api/file/cdn/2707322068/218668910222?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218668910222?contentType=1&isNewContent=false" nodeId="a8535204591f4bcbb8ce242c5a49de88"}![image.png](https://km.sankuai.com/api/file/cdn/2707322068/219749427375?contentType=1&isNewContent=false){width=140 height=117 small="https://km.sankuai.com/api/file/cdn/2707322068/219749427375?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/219749427375?contentType=1&isNewContent=false" nodeId="9bbed2489dd94c94bdd8f9d5be570c43"}![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218670532446?contentType=1&isNewContent=false){width=126 height=33 small="https://km.sankuai.com/api/file/cdn/2707322068/218670532446?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218670532446?contentType=1&isNewContent=false" nodeId="9d9d6e5ee7a849f293001f9ea54da66b"}
:::
:::
:::
:::table_row{nodeId="0dd337db29714009b66612cb0e55ff53"}
:::table_cell{colwidth="765" verticalAlign="middle" numCell=false nodeId="f67303fc72924b17b340c16bb67014cb"}
:::paragraph{nodeId="31e53de6f2be4fc9b0ea8baacea1dad5"}
现有组件因无法做到跨周期数据关联，系统无法自动唤起原签到用户提示下一场签到信息
:::

:::paragraph{nodeId="96df19fb02aa4d2488de1fb45ff1f09e"}
（仅依赖运营手动触达）
:::
:::
:::table_cell{colwidth="359" numCell=false nodeId="e12c47a630e3416584d07bc4d068e7fa"}
:::paragraph{nodeId="405e2d1dcb3e451d83335375904c2a6f"}
![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218667903384?contentType=1&isNewContent=false){width=115 height=117 small="https://km.sankuai.com/api/file/cdn/2707322068/218667903384?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218667903384?contentType=1&isNewContent=false" nodeId="2f0508a08d9c44b78ff522153d431a30"}![image.png](https://km.sankuai.com/api/file/cdn/2707322068/218672740477?contentType=1&isNewContent=false){width=96 height=120 small="https://km.sankuai.com/api/file/cdn/2707322068/218672740477?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/218672740477?contentType=1&isNewContent=false" nodeId="e917a7f8caa5464594d2cbe9a7ad1c4c"}
:::
:::
:::
:::

:::heading{level=2 nodeId="d864d32ba1354f5bb28d088234920ba1"}
3.26年中医营销规划
:::

:::paragraph{nodeId="b8a5ddf0505343d5805bdde3680a700d"}
26年依旧以24节气作为行业活动的主线，__玩法设计上保留25年的签到玩法，且通过签到活动升级，引导用户UGC内容宣发__。
:::

:::paragraph{nodeId="31dd03aa7e614c8eb968490b5ef0aeda"}
核心实现路径：期望通过__签到领奖__的方式引导用户加入私域群，同步发布「xx节气养生瞬间」，带话题#美团中医节气young生局#发布到小红书或大众点评，进行奖品和养生故事的分享。
:::

:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="bff33dda017d4181b0f5f35589e0a353"}
:::table_row{nodeId="edf9c0dc36d04fd59c5d224a97ee0514"}
:::table_header{colwidth="141" numCell=false nodeId="efd48ee3992f430792a2c35c2c20d8e3"}
:::paragraph{nodeId="fe97a6f32da946a29d5a342c1eb08a9c"}
:[font]{size=13}**整年节奏**[/font]
:::
:::
:::table_header{colwidth="113" numCell=false nodeId="e29e71e32df444bd8e454a070c0bb9bf"}
:::paragraph{nodeId="df877153c35e4955883764d358c4c484"}
:[font]{size=13}**活动级别**[/font]
:::
:::
:::table_header{colwidth="121" numCell=false nodeId="0e0630ea0b8d461f99dd06d790613da6"}
:::paragraph{nodeId="69e351eb5d1842838cbe47d1daa4af63"}
:[font]{size=13}**节气**[/font]
:::
:::
:::table_header{colwidth="151" numCell=false nodeId="10460f3bd30e46c496096467296c8c99"}
:::paragraph{nodeId="6c244802181b4f2b9e955e4fcfd852e1"}
:[font]{size=13}**活动时间**[/font]
:::
:::
:::
:::table_row{nodeId="203e81d723604e0ebaaaffd05a360437"}
:::table_cell{rowspan=9 colwidth="141" numCell=false nodeId="f89973b7e8b042b984bc2d53f65fa7c2"}
:::paragraph{nodeId="5a16c6eef9b6416a992396dc9bee86dd"}
:[font]{size=13}**24节气营销活动**[/font]
:::
:::
:::table_cell{colwidth="113" numCell=false nodeId="0933aec0ed1e4f8195366d96da7bfa81"}
:::paragraph{nodeId="7712572f924149128bc0c1dbcdeedea1"}
:[status]{pattern="fill" color="#FFD100" expand=true nodeId="e7ad861714b54c47ba1c5c559058a0c3"}A级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="6d03d41b76834d7684f532a2e8c5f2a7"}
:::paragraph{nodeId="408e9ae8133b4d5daf0a01474abccb52"}
春分（重要）
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="1f57341cc3084d309e3a7790340ad131"}
:::paragraph{nodeId="91aa20fbd9b941beb146652a1e5e363c"}
3.16～3.31
:::
:::
:::
:::table_row{nodeId="315703ef7bcc4cdabed0443d8a8da898"}
:::table_cell{colwidth="113" numCell=false nodeId="23494edf6324498dad2e4fe3ec695967"}
:::paragraph{nodeId="12a7c5370fef418a85d270bf00693329"}
:[status]{pattern="fill" color="#00BA73" expand=true nodeId="9e66c47ff6ee4a4c852d49dd40477041"}B级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="984c066b1ac64f69a8efd23dc811dc74"}
:::paragraph{nodeId="535286cfb4374b1fbe017deb90957884"}
谷雨
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="8a214c14c5e7418da3761f413b39e3bb"}
:::paragraph{nodeId="4572e62d43e94884b5e6e1821602c2b2"}
4.13～4.27
:::
:::
:::
:::table_row{nodeId="d879493838a5454ea9ceecac602fa954"}
:::table_cell{colwidth="113" numCell=false nodeId="4063174504964bf784028f175057b2a3"}
:::paragraph{nodeId="fd364a758bfa440ba245d7e56d8828bc"}
:[status]{pattern="fill" color="#FFD100" expand=true nodeId="d4a14cff96a645d780a54cd75245a49f"}A级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="908c2cc594cd43ba803bd352917e6f90"}
:::paragraph{nodeId="79153e6076db4755964d360da7620789"}
小满
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="5aad6e8d27d94ef2903ca4b9883f1f11"}
:::paragraph{nodeId="7b3035885bb04755b63ae106bfb6a216"}
5.13～5.24
:::
:::
:::
:::table_row{nodeId="98e1558ef21c44d3a66048c59de448c5"}
:::table_cell{colwidth="113" numCell=false nodeId="6336b6ddd0eb4add9bf5f5d37211f184"}
:::paragraph{nodeId="e9c7fcade5da4ec1b9e20921b7cf8d66"}
:[status]{pattern="fill" color="#FFD100" expand=true nodeId="722d1971db714e7aa3ad402e5d508a34"}A级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="2270a900d3764ba499f6cd1d8d2c80df"}
:::paragraph{nodeId="4a7e4c5a285f440e9d8431ad26c93d32"}
夏至
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="0628836482794434b2b26a45de97fc12"}
:::paragraph{nodeId="483d0e99063f4d0780da1089278ce2d8"}
6.13～6.28
:::
:::
:::
:::table_row{nodeId="ec07bc8d707942c3b5cf4b08c6907d66"}
:::table_cell{colwidth="113" numCell=false nodeId="92a4e844775446eb9f010981eb8b35c3"}
:::paragraph{nodeId="ee403c54855046cd9ac0d5fe8940fda6"}
:[status]{pattern="fill" color="#FF4A47" expand=true nodeId="1ae454b5893d463e8300b8b4b9a315ed"}S级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="2e98b918ddab4f04859e2b54916af54b"}
:::paragraph{nodeId="3bd2d7465eb047ec9030c5a2e1aa570a"}
三伏天
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="7c59bdc1ba584e29b2a205cb2e77c9ea"}
:::paragraph{nodeId="047444ed4f8944a69be05cbdbf306f19"}
7.6～8.24
:::
:::
:::
:::table_row{nodeId="ee96619c460e4d07bb0a9d0eb04254cd"}
:::table_cell{colwidth="113" numCell=false nodeId="9c82bbcd60a343919344ea6db3571fee"}
:::paragraph{nodeId="3f0d05ceadb545df8543292e6775b3f3"}
:[status]{pattern="fill" color="#00BA73" expand=true nodeId="cf18f4a592bc41ca85122fc233f6cfb5"}B级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="39788f3cc1784e69abf6ec562b2fcae8"}
:::paragraph{nodeId="eacb9f1047bc4dbcb5113930faaabb24"}
秋分
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="54d6c32036b94ecdbf0e847cb633bc95"}
:::paragraph{nodeId="189759fec8eb45dfb26cd366afdf3bef"}
9.16～9.30
:::
:::
:::
:::table_row{nodeId="adc57d0571a14d69b5ab00e41b6fb267"}
:::table_cell{colwidth="113" numCell=false nodeId="3eb4c7166e154384bde2c6d37a4262e4"}
:::paragraph{nodeId="0636cf804b9b4829b618c270b9db03fa"}
:[status]{pattern="fill" color="#FFD100" expand=true nodeId="d1e13372501e489ab3c7482aa6ab8ce9"}A级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="177f8ff7d9cc4280a9a6a80b18da6a6e"}
:::paragraph{nodeId="9688cbbc775742d49e6575572219d0ec"}
霜降
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="8f975fee30f2476ea6aa6afdd157bcf5"}
:::paragraph{nodeId="4b61dd6a6d14431991fdcb3eed602573"}
10.16～10.30
:::
:::
:::
:::table_row{nodeId="14b761986de6471d8862eb6fc3ca8374"}
:::table_cell{colwidth="113" numCell=false nodeId="174f583e5cff46bca37a464207e06106"}
:::paragraph{nodeId="2d08644a8e4d42ad8d9b145cbb6bf1d2"}
:[status]{pattern="fill" color="#00BA73" expand=true nodeId="008b2eab463846959ff3ec8325333237"}B级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="42d376285de145a28c58035ccba59752"}
:::paragraph{nodeId="bc0067ed33764d84be996d21c369e678"}
小雪
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="2dac46de51354281a19807abf9dd91c0"}
:::paragraph{nodeId="2e2ebee4e4f74d0cbfb9dbded62e02d6"}
11.16～11.30
:::
:::
:::
:::table_row{nodeId="c62063830e4e4bccba9e96684f3f865e"}
:::table_cell{colwidth="113" numCell=false nodeId="f6feb49902d2416da61e1c52032150f3"}
:::paragraph{nodeId="3d184767362e45cea086ec68ec59f3a7"}
:[status]{pattern="fill" color="#FFD100" expand=true nodeId="bdaccf6b14b54f23965bc1fea5cf7d66"}A级[/status]
:::
:::
:::table_cell{colwidth="121" numCell=false nodeId="dafef845f36147168d20737aa6e0256e"}
:::paragraph{nodeId="8e7e655a84ce43aba1893c696c0171a4"}
冬至
:::
:::
:::table_cell{colwidth="151" numCell=false nodeId="fa93aed7066b44969c6dfbbe580fbf5e"}
:::paragraph{nodeId="8a3fc0085f304c26be2c3a1a83f27229"}
12.15～12.29
:::
:::
:::
:::

:::heading{level=2 nodeId="c5f8fb9d3ecc4e57b198f04861c0c6b4"}
4.*26年中医节气签到近况
:::

:::paragraph{nodeId="df61ff5d6c484b08a2ab70f4e651da75"}
![](https://km.sankuai.com/api/file/cdn/2707322068/233489855809?contentType=1&isNewContent=false){width=630 height=236 small="https://km.sankuai.com/api/file/cdn/2707322068/233489855809?contentType=1&isNewContent=false" origin="https://km.sankuai.com/api/file/cdn/2707322068/233489855809?contentType=1&isNewContent=false" nodeId="ae4642518a584f4b9fa8d4cf53b29ae4"}
:::

:::paragraph{nodeId="8c2273f8de7b4e108a01978b4f5f2a18"}
**1）签到人数：**26年签到用户单场激增，YoY+331.66%
:::

:::paragraph{nodeId="de96eb36f9e947399d724f874d875de9"}
**2) 留存规模：**26年签到用户留存激增，企业微信活动社群已达1000人。
:::

:::paragraph{nodeId="5eb5237f57cd4606b8380409946e6cf9"}:::

:::heading{level=1 nodeId="0fd8ad7c451d4c09b430b9806f59f4ae"}
三.需求目标
:::

:::heading{level=2 nodeId="e33b4d8c1f704d8c9e21bc26d93747ad"}
1.定性目标
:::

:::paragraph{nodeId="0f79ddf61ee14004b41d2751d9f4e27e"}
通过建设【跨周期签到】营销组件产品能力，扩大中医意向人群留存，通过整年签到活动，实现用户高效私域留存、复访复购；增强用户对中医系列活动的持续关注度和行为粘性，培养“中医节气young生局”IP心智。
:::

:::heading{level=2 nodeId="08a70cfb58af435998f55a4eda3cf18f"}
2.定量目标
:::

:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="d28be9f45f7c4a30a83dc2acd49d4116"}
:::table_row{nodeId="34fad969c5254fd39d110a499a96ca2f"}
:::table_header{colwidth="216" nodeId="d1f81ed977e34bfa8f49493bcc4d3b8d"}
:::paragraph{nodeId="7f39fa841c9748d19e064c0edc955615"}:::
:::
:::table_header{colwidth="139" nodeId="2db3703c757e4f9b95019185dadb9918"}
:::paragraph{nodeId="acfe04f7c0b944258a7521c5d93d6cf1"}
每场活动
:::
:::
:::table_header{colwidth="188" nodeId="c859d1966bb649ddac231058dd80b043"}
:::paragraph{nodeId="70ba1290a6c5405bb09666d931f8e846"}
全年累计
:::
:::
:::
:::table_row{nodeId="f44ab39219264c5180c6ed7a79934e2c"}
:::table_cell{colwidth="216" nodeId="8d366360f799486e8b1255d5e6858315"}
:::paragraph{nodeId="136b74006e0d450a8fded3f7f0c9928f"}
签到目标
:::
:::
:::table_cell{colwidth="139" nodeId="124d2f9a6bda4d1cb9b534c393ebbd28"}
:::paragraph{nodeId="432468267e56497ead67cd6a2578cd0e"}
3w人/场
:::
:::
:::table_cell{colwidth="188" nodeId="e9892d822e544cf98b7a4242a7e45d99"}
:::paragraph{nodeId="60c3c87526694b8a9919a0b716adf266"}
27w人/年
:::
:::
:::
:::table_row{nodeId="7c3ae881147141ab84ca0e8f41f9daa2"}
:::table_cell{colwidth="216" nodeId="d923969e283d4db2ac024796bb3f2546"}
:::paragraph{nodeId="80a1b1912cef41219dc2bef35df41bd6"}
私域转化
:::
:::
:::table_cell{colwidth="139" nodeId="d69cb75fbe4c46559a6da27d4913f4e0"}
:::paragraph{nodeId="3d563dd92cec4b9fb222038628637881"}
300-500人/场
:::
:::
:::table_cell{colwidth="188" nodeId="4a4e649de2d44cde9e4fe874d3c471d7"}
:::paragraph{nodeId="57cee10db0274df9af5740de57712190"}
2,700-4,500人/年
:::
:::
:::
:::table_row{nodeId="4d9d33a36e574bcaa23046c6cf903001"}
:::table_cell{colwidth="216" numCell=false nodeId="23010f012c55450aab0bc78e8df1fe7f"}
:::paragraph{nodeId="34442a9fc2e44defb600b9edbb33cd14"}
新客目标
:::
:::
:::table_cell{colwidth="139" numCell=false nodeId="b95baa462e3349f384dd66f0517d4031"}
:::paragraph{nodeId="a5c94ee3e95e4202923869e4fb5b1144"}
24,510人/场
:::
:::
:::table_cell{colwidth="188" numCell=false nodeId="11dd61b8bf754027bdb1e922c191f4bd"}
:::paragraph{nodeId="33e53526d3ec476ca774d9e42a601821"}
220,590人/年
:::
:::
:::
:::table_row{nodeId="57357de0f1ef4b9dbcb3ac58f1da879c"}
:::table_cell{colwidth="216" numCell=false nodeId="725e0156a44f44419c615e43ebbe2c42"}
:::paragraph{nodeId="a0f9d0d4f87143c793fef7e3f2e65de6"}
签到后发布小红书笔记篇数
:::
:::
:::table_cell{colwidth="139" numCell=false nodeId="1843aa61d0d04aa596eaafcd7a8e6082"}
:::paragraph{nodeId="77bd69138b964b7eaee3548e6d2319cd"}
100篇/场
:::
:::
:::table_cell{colwidth="188" numCell=false nodeId="441deb75462949e7a8dd0ffefa41d39e"}
:::paragraph{nodeId="6c142c62c50d4a56b94a5835d23a2dcf"}
900篇/年
:::
:::
:::
:::

:::paragraph{nodeId="b86977745b2148ebae8b4fbedfe93911"}
 
:::

:::heading{level=1 nodeId="873dc7e2e3684721909a100d2ac78058"}
四.优化需求列表
:::

:::note{type=info nodeId="ae08d093352e4a54867b1bc71b35a9df" titleNodeId="1b720c55efc04e7fab2e2389b0c1062a" contentNodeId="34c7a3c2365845868ff4192f92336171"}

---
:::paragraph{nodeId="ebdee04d5cf947e191619685a2a232b7"}
**24节气young生局 26年签到规则**
:::

:::ordered_list{indent=0 nodeId="f09730b7011341d4ab3b4e64b075a14b"}
:::list_item{level=0 hidden=false nodeId="64dbd6190e8944d8a22bb401c80a1d2b"}
:::paragraph{nodeId="f6ffed955092463bb41c60a93a3987bb"}
2026年美团中医24节气活动整年共有**9场**，每场单次签到完成，均可获得【签到中医大额券：55-5元】（每人每次活动期间签到仅可领取1次）
:::
:::
:::list_item{level=0 hidden=false nodeId="f04d246e8ede455e993862c864a0feb7"}
:::paragraph{nodeId="375b3faace254b7fa914d7107f8639e4"}
**累计签到奖励：** 累积达到3次、5次、7次签到，即可解锁相应的**特别奖品**。（除春分外，签到须完成个人收货信息填写，方可获得领奖资格）
:::
:::
:::list_item{level=0 hidden=false nodeId="6326cb3444824c568c014c4de7b14471"}
:::paragraph{nodeId="bc689c4a45b046159341a509a21d0918"}
**连续签到大奖：** 连续9次活动不间断签到，100%可获神秘【大奖惊喜】
:::
:::
:::
:::

:::heading{level=2 nodeId="a2b9af4a53c543c58bac6ae181f8d735"}
1.需求明细
:::

:::table{borderColor="#dddddd" borderStyle="solid" borderWidth=1 responsive=false nodeId="88801108dbf6449a935b90de2d333421"}
:::table_row{nodeId="9f2f0d69a45a40bbae55364e5545eb12"}
:::table_header{colwidth="202" numCell=false nodeId="f023f658332641299bfba9cc76087e40"}
:::paragraph{nodeId="26dab7d5ab1e42deb509947a3784d6f5"}
签到组件需求
:::
:::
:::table_header{colwidth="703" numCell=false nodeId="13ea5c7e12e149d887077a84b577bd1b"}
:::paragraph{nodeId="affcc560ff46458f9b45f5b1f8fef0d2"}
描述
:::
:::
:::
:::table_row{nodeId="f39350147b234499b91111f0a7f77bd7"}
:::table_cell{colwidth="202" numCell=false nodeId="b7e1fd68dda4479291ed578d6194716b"}
:::paragraph{nodeId="930ba605d0de415e95c6b6b181230770"}
**1.实现跨周期签到**
:::
:::
:::table_cell{colwidth="703" numCell=false nodeId="b7906cbb09e246099ff145dce0f8e56c"}
:::paragraph{nodeId="22e0d775160d4a1599e18592e0a79f87"}
:[font]{size=13}春分 ：2026-3-16至2026-3-31  活动期间内签到，累计签到成功1次[/font]
:::

:::paragraph{nodeId="cb1b1827c3854853b0e6507c07de3e6d"}
:[font]{size=13}谷雨： 2026-4-13至2025-4-27 活动期间内签到，累计签到成功2次[/font]
:::

:::paragraph{nodeId="0d614bac7afd4a4bbff714923def3fc8"}
:[font]{size=13}小满： 2026-5-13至2026-5-24活动期间内签到，累计签到成功3次[/font]
:::

:::paragraph{nodeId="ec80b5e6ca1a40788bd6cb4b5827c0da"}
:[font]{size=13}.... [/font]
:::
:::
:::
:::table_row{nodeId="10610db8e680410f932dcc330f5b931d"}
:::table_cell{colwidth="202" numCell=false nodeId="d371c36209254a3eac94a44e4616d7b5"}
:::paragraph{nodeId="321dbf0fe98c413480b687425a88df1c"}
**2.任务触发签到**
:::
:::
:::table_cell{colwidth="703" numCell=false nodeId="7a360f13048347f39e147a9445006696"}
:::paragraph{nodeId="f2b7d2b889754b62a1344db4274e063e"}
:[font]{size=13}签[/font]:[font]{size=13}:[quote]{quoteId="2707322068--1175bd13-643e-4ea2-91ab-3d7be7805208"}到前提条件：[/quote][/font]:[font]{size=13}（随着活动推进，奖品加码，对应的签到门槛相应增加，签到需要满足对应的任务）[/font]
:::

:::paragraph{nodeId="a39b0fdce1b74e9b872bf5ce79dddf74"}
:[font]{size=13}①[/font]:[font]{size=13}:[quote]{quoteId="2707322068--1175bd13-643e-4ea2-91ab-3d7be7805208"}用户完成≥1次活动页内下单，获得1次签到[/quote][/font]:[font]{size=13}机会[/font]
:::

:::paragraph{nodeId="bbb52fdb1cc64d808678ca8f36a5cc4f"}
:[font]{size=13}②用户完成≥1次活动页分享，获得1次签到机会[/font]
:::
:::
:::
:::table_row{nodeId="ca5453dbdcd74718bf2ab9497eaac767"}
:::table_cell{colwidth="202" numCell=false nodeId="810bce7fd2b44edbaa5b8caf8f4ae1af"}
:::paragraph{nodeId="8236c2321f6f439a809b8ded0eba191d"}
**3.签到留资关联**
:::
:::
:::table_cell{colwidth="703" numCell=false nodeId="980f437aaffe49f28aac8af4f4f7082b"}
:::paragraph{nodeId="9a6a0f945adc4955b14daddbeac51f16"}
:[font]{size=13}签到完成后可实现用户信息留资：签到成功的用户可以立即留下姓名、联系方式、收货地址，用于实物奖品的邮寄[/font]
:::
:::
:::
:::table_row{nodeId="8933991074cc4f2b808ab551b156c219"}
:::table_cell{colwidth="202" numCell=false nodeId="8d96cb659fbd4b90aeec33977af94638"}
:::paragraph{nodeId="be649b2001164fddb496bbfaad18b8ac"}
**4.累计签到次数显示——“我的奖品”模块**
:::
:::
:::table_cell{colwidth="703" numCell=false nodeId="ee9c4da9c54a41e6b50b14cb43ef7f8e"}
:::paragraph{nodeId="338a07345fe743e680e75a63e0487af0"}
:[font]{size=13}用户签到完成后有入口可查询总计签到次数、获得的签到奖品、奖品物流信息[/font]
:::
:::
:::
:::table_row{nodeId="4a42b50510ef412fac46279f8d821afe"}
:::table_cell{colwidth="202" numCell=false nodeId="c2e0e7ca025948858b534fe5a0d57412"}
:::paragraph{nodeId="abb715ed52394dd091cc362aec8cecfc"}
**5.签到数据记录**
:::
:::
:::table_cell{colwidth="703" numCell=false nodeId="1c5bdc9497b04118a9e08d9d8d87ecaa"}
:::paragraph{nodeId="7d3346849d894e51bbdc64e101bbe12f"}
:[font]{size=13}签到组件需记录：每个用户签到明细（用户活动累计签到次数/用户userid/签到获得奖品...）[/font]
:::
:::
:::
:::

:::heading{level=2 nodeId="fd502ac78a154af7a4f30063666ae9c0"}
2.交互流程
:::

:::drawio{src="https://km.sankuai.com/api/file/cdn/2707322068/219744970245?contentType=0&isNewContent=false" width=1105 height=898 nodeId="9ac85625ecbc4e4ab05d88567e6899ac"}:::

:::appendix{nodeId="1afdf2953ee5469c9b01366576ef4e21"}:::

:::collapse{nodeId="4ab92efd1246459b8a1519d102ac9cb8" titleNodeId="cd24ba8a7f7f40c3bfaa54e3c301dd02" contentNodeId="86af3287993444a89d0a36444a951cf7"}
签到新客sql
---
:::paragraph{nodeId="016c667293b64f65adf8208fae97aa63"}
SELECT COUNT(DISTINCT c.userid) AS new_customer_count
:::

:::paragraph{nodeId="e4d4cdd8be7b49179a65f4be93b5ad66"}
FROM (
:::

:::paragraph{nodeId="867ef94efc514d9b8126605d9f22c8bc"}
    -- 领券用户
:::

:::paragraph{nodeId="8bf2df40489746a28de25622284c26c2"}
    SELECT userid
:::

:::paragraph{nodeId="9c6144c829b44bc2869c4b5c348dac2c"}
    FROM log.wpt_cube_send_coupon_record
:::

:::paragraph{nodeId="29d213622def48cfb20823026266e767"}
    WHERE playwayid IN (144089,148115,154168,160030,165257,167498,171541)
:::

:::paragraph{nodeId="708163b69fce411ab3f191143db00283"}
      AND dt >= '20250415'
:::

:::paragraph{nodeId="f4c6bc0dfd9947cdb5c8da3a64e0af9a"}
      AND dt <= '20251226'
:::

:::paragraph{nodeId="2a9afaa239d64d4f970a446facb8a864"}
) c
:::

:::paragraph{nodeId="d609add1ff564970befae8d46abb283b"}
LEFT JOIN (
:::

:::paragraph{nodeId="6432d4cae498429bb38f64b56626bac4"}
    -- 过去一年在中医机构有交易的用户
:::

:::paragraph{nodeId="fc40dd9715fd44c29e7784a47373d069"}
    SELECT DISTINCT mt_user_id
:::

:::paragraph{nodeId="4f9ba0dd436f45f0b870538d973c60f3"}
    FROM mart_med_health.fact_ord_general_wide_trade_buy_order_d_inc
:::

:::paragraph{nodeId="4886c0160b654ec48613b50f0d085ba8"}
    WHERE bizln_cat1_name = '中医机构'
:::

:::paragraph{nodeId="5916c909dfad48bc913f76a819d56e26"}
      AND dt >= '20240415'
:::

:::paragraph{nodeId="55112de502c74f9f8f47d6e1ae932b78"}
      AND dt <= '20250414'
:::

:::paragraph{nodeId="b82a6c348a7144e4839cd5a8b445fa2f"}
) t
:::

:::paragraph{nodeId="920379d78c104d6f927eeceaa517d8fd"}
ON c.userid = t.mt_user_id
:::

:::paragraph{nodeId="4ae1ce69b9ec40e8869763240d3fe5c1"}
WHERE t.mt_user_id IS NULL
:::
:::

:::collapse{nodeId="b9aa400888ec417eb7b807740521aa04" titleNodeId="3d1648a7b16d4f5ebb1fa05ca4166811" contentNodeId="6a4680e467eb4500abbddab2f5df0f2d"}
签到新客复购sql
---
:::paragraph{nodeId="0fac2a5b6dee47e293cb06ce4e02d3d6"}
SELECT COUNT(DISTINCT o.mt_user_id) AS active_new_customer_count
:::

:::paragraph{nodeId="963b0ea3a50b43099056683333dfe231"}
FROM (
:::

:::paragraph{nodeId="5cff65596f6946b3902b8df80481b065"}
    -- 新客用户明细
:::

:::paragraph{nodeId="5f87cde39b4b43f2b9b6bd7fcf3a8b9f"}
    SELECT c.userid
:::

:::paragraph{nodeId="71602631a1474c05ba08be8312843827"}
    FROM (
:::

:::paragraph{nodeId="5606ca71ec3a42aeacf4491417011d32"}
        SELECT userid
:::

:::paragraph{nodeId="838b8b0a495e49d78eef093aff3f7dc2"}
        FROM log.wpt_cube_send_coupon_record
:::

:::paragraph{nodeId="d332f27504b24ecb923107b598633c64"}
        WHERE playwayid IN (144089,148115,154168,160030,165257,167498,171541)
:::

:::paragraph{nodeId="9d50f5c9cdd743a1a35c54c1c524fce4"}
          AND dt >= '20250415'
:::

:::paragraph{nodeId="f2fa48995801496481eb63b8230f3e83"}
          AND dt <= '20251226'
:::

:::paragraph{nodeId="4133018c07c74c989596440c11df5ccc"}
    ) c
:::

:::paragraph{nodeId="e7a87183131c4ad491dc9800ad32c7c9"}
    LEFT JOIN (
:::

:::paragraph{nodeId="f19d32a0ae4741cc8a26ad72ad1ac320"}
        SELECT DISTINCT mt_user_id
:::

:::paragraph{nodeId="4ad81c58ee904d49866d137a34efb01f"}
        FROM mart_med_health.fact_ord_general_wide_trade_buy_order_d_inc
:::

:::paragraph{nodeId="2890b239a6c74a948f654089869448f3"}
        WHERE bizln_cat1_name = '中医机构'
:::

:::paragraph{nodeId="143f4b80e0974e398f8824a166eb33d1"}
          AND dt >= '20240415'
:::

:::paragraph{nodeId="364d5199563c4e1abe9c772c03b0b108"}
          AND dt <= '20250414'
:::

:::paragraph{nodeId="377d5a9124d543d78481106d1934caaf"}
    ) t
:::

:::paragraph{nodeId="205ae6fcaff24802a3f46f3d827d41f2"}
    ON c.userid = t.mt_user_id
:::

:::paragraph{nodeId="b433fc0c667a4711ae186b818a5490f9"}
    WHERE t.mt_user_id IS NULL
:::

:::paragraph{nodeId="f289dde2c3014087a5ff5d72c0a4f148"}
) newcus
:::

:::paragraph{nodeId="b5db1a9a9ed34097af546d6172711295"}
JOIN (
:::

:::paragraph{nodeId="d52a88e847764f82ae27a84b8209e750"}
    -- 统计新客在中医机构的交易次数
:::

:::paragraph{nodeId="7328aba349c745148c5428cf75a36632"}
    SELECT mt_user_id
:::

:::paragraph{nodeId="456ba4df1f3e47689429be6025e55c59"}
    FROM mart_med_health.fact_ord_general_wide_trade_buy_order_d_inc
:::

:::paragraph{nodeId="36361ff1a47042579b0790efec7f5214"}
    WHERE bizln_cat1_name = '中医机构'
:::

:::paragraph{nodeId="229257707ca449b6846072834430a953"}
      AND dt >= '20250415'
:::

:::paragraph{nodeId="a23cd926a5b4401792cf7231f0179ee5"}
      AND dt <= '20260122'
:::

:::paragraph{nodeId="c6382c9a462e49d197fad8413c372200"}
    GROUP BY mt_user_id
:::

:::paragraph{nodeId="d771a2a53ae54db893f82198ca169c7d"}
    HAVING COUNT(*) >= 1
:::

:::paragraph{nodeId="51658b9743d74741b6cc056da58af156"}
) o
:::

:::paragraph{nodeId="14af7d3fc0e942d88b61efa4312774de"}
ON newcus.userid = o.mt_user_id
:::
:::

:::footnote_list{nodeId="3332fe9361bb457fa0f9c9ce679506df"}
:::footnote_list_item{footnoteNodeId="f39526a2526844ee83e3b366954a441d" nodeId="d537826fa99a463dbe6eaf98ad586cfb"}
:::paragraph{nodeId="91e044986511407cb7d9c775d52aa0f3"}
新客：在25年3月签到开启前1年内没有中医交易行为的签到用户
:::
:::
:::footnote_list_item{footnoteNodeId="cc5fcd7546324939ad42cb893446b993" nodeId="3df7d251b99d45458e5e35fa1ab57612"}
:::paragraph{nodeId="4f90bf1b5da7407fade1e3ae5edfe0bf"}
复购：签到新客从3月签到开启后，累计至今，交易次数>1的用户
:::
:::
:::
