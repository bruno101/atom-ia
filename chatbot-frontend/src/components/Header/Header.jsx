import React from "react";
import { BrHeader, BrBreadcrumbs, BrDivider } from "@govbr-ds/react-components";

const Header = () => {
  return (
    <><BrHeader signature={"Ministério da Gestão e da Inovação em Serviços Públicos"} quickAccessLinks={[
      {
        "label": "Órgãos do Governo"
      },
      {
        "label": "Acesso à Informação"
      },
      {
        "label": "Legislação"
      },
      {
        "label": "Acessibilidade"
      }
    ]}
    urlLogo={"https://www.gov.br/ds/assets/img/govbr-logo.png"} features={[
      {
        "label": "Funcionalidade 1",
        "icon": "cookie-bite"
      },
      {
        "label": "Funcionalidade 2",
        "icon": "th"
      },

      {
        "label": "Funcionalidade 4",
        "icon": "adjust"
      }
    ]} showMenuButton={true} showSearchBar={true} title={"Arquivo Nacional"} fluid={"xl"}    ></BrHeader>
    <BrDivider/>
    </>
  );
};

export default Header;
