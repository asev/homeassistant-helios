from homeassistant import config_entries
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

import eazyctrl

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CONF_HOST,
    CONF_NAME
)

class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    @property
    def schema(self):
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): str,
            }
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_NAME])
            self._abort_if_unique_id_configured()

            try:
                client = eazyctrl.EazyController(user_input[CONF_HOST])
                device = client.get_variable("v00000", 30)
            except:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self.schema,
                    errors={"base": "invalid_host"}
                )

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input
            )

        return self.async_show_form(step_id="user", data_schema=self.schema)
