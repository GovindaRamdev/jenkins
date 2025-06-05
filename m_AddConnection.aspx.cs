using Newtonsoft.Json;
using OnNetSinglePlay.App_Code;
using OnNetSinglePlayLib;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Web;
using System.Web.Services;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Xml;
 
namespace OnNetSinglePlay.RstSubscriber
{
    public partial class m_AddConnection : BasePage
    {
        protected void Page_Load(object sender, EventArgs e)
        {
            if (!IsPostBack)
            {
                clsSubscriber objSubscriber = new clsSubscriber();
                objSubscriber._CurrMenuID = (long)enmMenuItemsName.mnuSubsAddNewConn;
                string MenuData = GetMenuData(Convert.ToInt32(enmMenuItemsName.mnuSubsAddNewConn));
                DataSet dsForm_Property = objSubscriber.Proc_Form_Property_ForSubscriber();
                DataTable dtProp = objSubscriber.FormProperty_H_SelectAll(" AND PropID IN (557) ");        //RSOFT-55532
                ScriptManager.RegisterStartupScript(this, this.GetType(), "setAddConnectionData", "javascript:setAddConnectionData('" + MenuData + "','" + JsonConvert.SerializeObject(objSubscriber) + "','" + checkOTTModuleHave().ToString() + "','" + JsonConvert.SerializeObject(dsForm_Property) + "','" + JsonConvert.SerializeObject(dtProp) + "');", true);
            }
        }
    }
}
