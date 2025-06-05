<%@ Page Title="" Language="C#" MasterPageFile="~/Main.Master" AutoEventWireup="true" CodeBehind="m_AddConnection.aspx.cs" Inherits="OnNetSinglePlay.RstSubscriber.m_AddConnection" %>
 
<asp:Content ID="Content1" ContentPlaceHolderID="head" runat="server">
<script src="../RstScripts/RstForm/m_AddConnection.js?v=<%= System.Configuration.ConfigurationManager.AppSettings["JSVersion"] %>.01"></script>
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="server">
<div class="FormBtnDiv">
<div class="btncnt">
<button data-icon="Reset" class="btnCls rel-ic-reset" onclick="javascript:buttonpulse(this, event);AddConnectionReset(); return false;" tabindex="2">Reset</button>
</div>
 
    </div>
 
    <div id="dialogState">
<div class="FormContent">
<div class="Grid" style="margin-top: 40px;">
<div id="DyGrid">
</div>
</div>
<input type="hidden" id="HSubscriberCompID" value="0"/>
<label id="lblEditRegistrationDate" style="display:none"></label>
</div>
</div>
</asp:Content>
