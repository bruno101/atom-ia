import React from "react";
import { BrFooter } from "@govbr-ds/react-components";

const Footer = () => {
    return <><BrFooter socialNetworks={[
        {
          "name": "Facebook",
          "link": "#",
          "icon": "fab fa-facebook-square"
        },
        {
          "name": "Twitter",
          "link": "#",
          "icon": "fab fa-twitter-square"
        },
        {
          "name": "Linkedin",
          "link": "#",
          "icon": "fab fa-linkedin"
        }
      ]} links={[
        {
          "category": "Categoria 1",
          "items": [
            {
              "label": "Ad deserunt nostrud",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            }
          ]
        },
        {
          "category": "Categoria 2",
          "items": [
            {
              "label": "Ex qui laborum consectetur aute commodo",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            },
            {
              "label": "Ex qui laborum consectetur aute commodo",
              "link": "#"
            }
          ]
        },
        {
          "category": "Categoria 3",
          "items": [
            {
              "label": "Ad deserunt nostrud",
              "link": "#"
            },
            {
              "label": "Ex qui laborum consectetur aute commodo",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            }
          ]
        },
        {
          "category": "Categoria 4",
          "items": [
            {
              "label": "Ad deserunt nostrud",
              "link": "#"
            },
            {
              "label": "Ex qui laborum consectetur aute commodo",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            }
          ]
        },
        {
          "category": "Categoria 5",
          "items": [
            {
              "label": "Ex qui laborum consectetur aute commodo",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            }
          ]
        },
        {
          "category": "Categoria 6",
          "items": [
            {
              "label": "Ex qui laborum consectetur aute commodo",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            },
            {
              "label": "Nulla occaecat eiusmod",
              "link": "#"
            }
          ]
        }
      ]}/></>;
}

export default Footer;
