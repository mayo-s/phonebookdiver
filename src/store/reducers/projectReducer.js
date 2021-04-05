const initState = {
    projects: [
        {id: '42', title: 'Welcome', content: 'The project The Phone Book Diver provides several tools to analyze and visualize data from 25 years of public German telephone books. These tools can be used to display the distribution of names on a heatmap, search and merge the data across multiple editions, and perform further analysis using a Jupyter Notebook.', author: 'Mario', timestamp: '4th April, 2021'},
        {id: '1111', title: 'Thank you', content: 'Special credits to Prof. Weber-Wulff from the University of Applied Sciences Berlin and Erdgeist for the project support and the provision of the telephone book data.', author: 'Mario', timestamp: '6th April, 2021'},
        {id: '1337', title: 'License', content: 'Unless otherwise stated, this project is licensed under CC-BY 4.0.', author: 'Mario', timestamp: '6th April, 2021'}
    ]
}

const projectReducer = (state = initState, action) => {
  return state
}

export default projectReducer