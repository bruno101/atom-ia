// Header.jsx
import React from "react";
import { BrHeader } from "@govbr-ds/react-components";

const Header = () => {
  return (
    <BrHeader signature={"SIAN"} quickAccessLinks={[
      {
        "label": "Acesso Rápido 1"
      },
      {
        "label": "Acesso Rápido 2"
      }
    ]}
    urlLogo={"https://www.gov.br/ds/assets/img/govbr-logo.png"} features={[
      {
        "label": "Funcionalidade 1",
        "icon": "chart-bar"
      },
      {
        "label": "Funcionalidade 2",
        "icon": "headset"
      },
      {
        "label": "Funcionalidade 3",
        "icon": "comment"
      },
      {
        "label": "Funcionalidade 4",
        "icon": "adjust"
      }
    ]} showMenuButton={true} showSearchBar={true} title={"Chatbot SIAN"} subTitle={"Chatbot do Sistema de Informações do Arquivo Nacional"}></BrHeader>
  );
};

export default Header;
