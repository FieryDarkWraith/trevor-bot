# Trevor 
> "Top Overall Hack" in CodeDay NY 2017 (February 17 - February 18)

By Nancy Cao, Kevin Zhang, Celine Yan

### Purpose

Meet Trevor, the Facebook Messenger Bot that connects clients who need legal advice with legal advisors who want to volunteer free legal service and provide answers. Trevor serves as a pipe for conversation between the Client and the Volunteer, echoing messages to and from it. It is a identity barrier that prevents either user from identifying the other. This is an essential component that protects the anonymity of clients and volunteers, which avoids bias in answers and promotes equal and standard answers for clients of different sex, race, ethnicity, etc.

The inspiration for this project stems from the controversial immigration ban implemented by executive order of President Trump on January 27, 2017. With so many lawyers and legal advisors who converged to numerous protests around the globe and provided legal advice to those who needed it, we created prototype bot Trevor who lives on Facebook, a popular social media platform worldwide, to facilitate these exchanges virtually. 

### Focus

In this hack, we provided three main legal topics to choose from for clients: 

1. Immigration Laws
2. Citizenship
3. VISA

### Technicalities

We utilized the Facebook Messenger Bot API and programmed using Python in a Python Wrapper provided by Hartly Brody. We retained Client and Volunteer input information in a SQLite database. In order to test our code, we were required to deploy using Heroku. 

### Future Implementations

- Expand to International Scale
  - Not only limited to the United States; legal advisors from all over the globe can provide specific legal advice to specific clients, depending on certain laws in certain countries.
- Language
  - Clients can select what language they wish to converse in.
- Ratings
  - Clients may rate the conversation after calling 'STOP'.
  - Legal advisors with high ratings will be prioritized to future clients. 


*readme.md by Celine Yan*
*Facebook Messenger Bot forked from hartleybrody/fb-messenger-bot*

