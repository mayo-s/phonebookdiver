const initState = {
    projects: [
        {id: '42', title: 'Welcome', content: 'The Phone Book Diver project visualizes the distribution of names and further more merges records from 25 years of telephone book data.', author: 'Mario', timestamp: '6th April, 2021'},
        {id: '1111', title: 'Thank you', content: 'Special credits to Prof. Weber-Wulff from the University of Applied Sciences Berlin and Erdgeist for the project support and the provision of the telephone book data.', author: 'Mario', timestamp: '6th April, 2021'},
        {id: '1337', title: 'License', content: 'Unless otherwise stated, this project is licensed under CC-BY 4.0.', author: 'Mario', timestamp: '6th April, 2021'}
    ]
}

const projectReducer = (state = initState, action) => {
  return state
}

export default projectReducer